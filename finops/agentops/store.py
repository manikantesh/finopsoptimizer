"""
SQLite-backed persistence for AgentOps traces, cost rollups, and alerts.

Kept deliberately simple (stdlib sqlite3, one file, one lock) to match a
"0-6mo, see it" phase -- swapping the backend later means replacing this one
class, since everything else in the package talks to the store through
these methods only.
"""

import json
import logging
import os
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

from .models import Alert, AlertSeverity, Event, EventType, new_id
from .pricing import TokenPricingCalculator

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    started_at REAL NOT NULL,
    ended_at REAL,
    status TEXT NOT NULL DEFAULT 'open',
    total_cost REAL NOT NULL DEFAULT 0,
    call_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    turn_id TEXT,
    payload TEXT NOT NULL,
    cost REAL NOT NULL DEFAULT 0,
    timestamp REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    rule TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    session_id TEXT,
    created_at REAL NOT NULL,
    root_cause TEXT
);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at);
"""


class TraceStore:
    """Persists agent sessions/events/alerts and keeps running cost rollups."""

    def __init__(self, db_path: str, pricing: Optional[TokenPricingCalculator] = None):
        self.db_path = db_path
        self.pricing = pricing or TokenPricingCalculator()
        self._lock = threading.RLock()
        os.makedirs(os.path.dirname(os.path.abspath(db_path)) or ".", exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.executescript(SCHEMA)
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # -- writes ---------------------------------------------------------

    def record_event(self, event: Event) -> Optional[float]:
        """Persist an event, updating the parent session's rollups. Returns cost if any."""
        cost = 0.0
        if event.event_type == EventType.LLM_CALL:
            model = event.payload.get("model", "unknown")
            input_tokens = int(event.payload.get("input_tokens", 0))
            output_tokens = int(event.payload.get("output_tokens", 0))
            cost = self.pricing.cost(model, input_tokens, output_tokens)

        with self._lock:
            self._ensure_session(event)

            self._conn.execute(
                "INSERT OR REPLACE INTO events "
                "(event_id, session_id, event_type, turn_id, payload, cost, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    event.event_id,
                    event.session_id,
                    event.event_type.value,
                    event.turn_id,
                    json.dumps(event.payload),
                    cost,
                    event.timestamp,
                ),
            )

            if event.event_type == EventType.LLM_CALL:
                self._conn.execute(
                    "UPDATE sessions SET total_cost = total_cost + ?, call_count = call_count + 1 "
                    "WHERE session_id = ?",
                    (cost, event.session_id),
                )
            elif event.event_type == EventType.ERROR:
                self._conn.execute(
                    "UPDATE sessions SET error_count = error_count + 1, status = 'error' "
                    "WHERE session_id = ?",
                    (event.session_id,),
                )
            elif event.event_type == EventType.SESSION_END:
                status = event.payload.get("status", "closed")
                self._conn.execute(
                    "UPDATE sessions SET ended_at = ?, status = CASE WHEN status = 'error' "
                    "THEN status ELSE ? END WHERE session_id = ?",
                    (event.timestamp, status, event.session_id),
                )

            self._conn.commit()

        return cost or None

    def _ensure_session(self, event: Event) -> None:
        row = self._conn.execute(
            "SELECT 1 FROM sessions WHERE session_id = ?", (event.session_id,)
        ).fetchone()
        if row is None:
            self._conn.execute(
                "INSERT INTO sessions (session_id, agent_id, channel, started_at, status) "
                "VALUES (?, ?, ?, ?, 'open')",
                (event.session_id, event.agent_id, event.channel.value, event.timestamp),
            )

    def insert_alert(self, alert: Alert) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO alerts (alert_id, rule, severity, message, session_id, created_at, root_cause) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    alert.alert_id,
                    alert.rule,
                    alert.severity.value,
                    alert.message,
                    alert.session_id,
                    alert.created_at,
                    alert.root_cause,
                ),
            )
            self._conn.commit()

    def set_alert_root_cause(self, alert_id: str, root_cause: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE alerts SET root_cause = ? WHERE alert_id = ?", (root_cause, alert_id)
            )
            self._conn.commit()

    # -- reads ------------------------------------------------------------

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if row is None:
                return None
            events = self._conn.execute(
                "SELECT * FROM events WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            ).fetchall()
        session = dict(row)
        session["events"] = [self._event_row_to_dict(e) for e in events]
        return session

    def list_sessions(self, limit: int = 50, since: Optional[float] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM sessions"
        params: List[Any] = []
        if since is not None:
            query += " WHERE started_at >= ?"
            params.append(since)
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def list_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def window_stats(self, window_seconds: float) -> Dict[str, Any]:
        """Aggregate stats over the trailing window, used by the alert engine."""
        cutoff = time.time() - window_seconds
        with self._lock:
            cost_row = self._conn.execute(
                "SELECT COALESCE(SUM(cost), 0) AS cost, COUNT(*) AS calls "
                "FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.LLM_CALL.value, cutoff),
            ).fetchone()
            error_row = self._conn.execute(
                "SELECT COUNT(*) AS errors FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.ERROR.value, cutoff),
            ).fetchone()
            session_row = self._conn.execute(
                "SELECT COUNT(*) AS sessions FROM sessions WHERE started_at >= ?",
                (cutoff,),
            ).fetchone()
            latency_rows = self._conn.execute(
                "SELECT payload FROM events WHERE event_type = ? AND timestamp >= ?",
                (EventType.LLM_CALL.value, cutoff),
            ).fetchall()

        latencies = []
        for r in latency_rows:
            payload = json.loads(r["payload"])
            if "latency_ms" in payload:
                latencies.append(payload["latency_ms"])
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95) - 1] if latencies else 0

        return {
            "window_seconds": window_seconds,
            "cost": cost_row["cost"],
            "llm_calls": cost_row["calls"],
            "errors": error_row["errors"],
            "sessions": session_row["sessions"],
            "latency_p95_ms": p95,
        }

    def recent_error_messages(self, window_seconds: float, limit: int = 50) -> List[str]:
        """Error messages from the trailing window, most recent first -- for RCA."""
        cutoff = time.time() - window_seconds
        with self._lock:
            rows = self._conn.execute(
                "SELECT payload FROM events WHERE event_type = ? AND timestamp >= ? "
                "ORDER BY timestamp DESC LIMIT ?",
                (EventType.ERROR.value, cutoff, limit),
            ).fetchall()
        messages = []
        for r in rows:
            payload = json.loads(r["payload"])
            messages.append(payload.get("message", "unknown error"))
        return messages

    def recent_llm_models(self, window_seconds: float, limit: int = 200) -> List[str]:
        """Model names used by LLM calls in the trailing window -- for RCA."""
        cutoff = time.time() - window_seconds
        with self._lock:
            rows = self._conn.execute(
                "SELECT payload FROM events WHERE event_type = ? AND timestamp >= ? "
                "ORDER BY timestamp DESC LIMIT ?",
                (EventType.LLM_CALL.value, cutoff, limit),
            ).fetchall()
        models = []
        for r in rows:
            payload = json.loads(r["payload"])
            models.append(payload.get("model", "unknown"))
        return models

    @staticmethod
    def _event_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        d["payload"] = json.loads(d["payload"])
        return d
