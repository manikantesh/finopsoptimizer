"""
Python SDK for instrumenting an agent: ``AgentSession`` + ``Turn`` context managers.

Works two ways, so the same code integrates with anything:

- **Embedded** (default): events are written straight to a local ``TraceStore``
  (SQLite file). No server required -- good for a single process.
- **Remote**: pass ``server_url`` and events are translated to OTLP and
  POSTed to a running ``agentops serve`` instance's ``/v1/traces`` endpoint --
  the same OpenTelemetry-only ingestion contract that non-Python agents
  (voice/text/web, any language) use directly -- see docs/agent-observability.md.

Example::

    from finops.agentops import AgentSession

    with AgentSession(agent_id="support-bot", channel="voice") as session:
        with session.turn(user_input="what's my balance?") as turn:
            turn.log_llm_call(model="claude-sonnet-5", input_tokens=180, output_tokens=64, latency_ms=420)
            turn.log_tool_call(name="lookup_balance", ok=True)
"""

import logging
import threading
import time
from typing import Any, Dict, Optional

from .models import Channel, Event, EventType, new_id
from .otlp import event_to_otlp_payload
from .paths import DEFAULT_DB_PATH
from .store import TraceStore

logger = logging.getLogger(__name__)

_default_store: Optional[TraceStore] = None
_default_store_lock = threading.Lock()


def get_default_store(db_path: str = DEFAULT_DB_PATH) -> TraceStore:
    """Process-wide singleton store used when no store/server_url is given."""
    global _default_store
    with _default_store_lock:
        if _default_store is None:
            _default_store = TraceStore(db_path)
        return _default_store


class _EventSink:
    """Sends events either to an embedded TraceStore or a remote server."""

    def __init__(self, store: Optional[TraceStore], server_url: Optional[str]):
        self.store = store
        self.server_url = server_url.rstrip("/") if server_url else None

    def send(self, event: Event) -> None:
        if self.server_url:
            otlp_payload = event_to_otlp_payload(event)
            if otlp_payload is None:
                return  # session/turn lifecycle marker: nothing to send over OTLP
            try:
                import requests

                requests.post(f"{self.server_url}/v1/traces", json=otlp_payload, timeout=5)
            except Exception as exc:  # network/agent code must never crash on telemetry
                logger.warning("agentops: failed to send event to %s: %s", self.server_url, exc)
            return

        store = self.store or get_default_store()
        try:
            store.record_event(event)
        except Exception as exc:
            logger.warning("agentops: failed to record event: %s", exc)


class Turn:
    """A single conversational turn within an ``AgentSession``."""

    def __init__(self, sink: _EventSink, session_id: str, agent_id: str, channel: Channel,
                 user_input: Optional[str] = None):
        self._sink = sink
        self.session_id = session_id
        self.agent_id = agent_id
        self.channel = channel
        self.turn_id = new_id("turn")
        self.user_input = user_input

    def __enter__(self) -> "Turn":
        self._emit(EventType.TURN_START, {"user_input": self.user_input})
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc is not None:
            self.log_error(str(exc), error_type=exc_type.__name__ if exc_type else "Exception")
        self._emit(EventType.TURN_END, {})

    def log_llm_call(self, model: str, input_tokens: int, output_tokens: int,
                      latency_ms: Optional[float] = None, **extra: Any) -> None:
        payload = {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            **extra,
        }
        self._emit(EventType.LLM_CALL, payload)

    def log_tool_call(self, name: str, **extra: Any) -> None:
        self._emit(EventType.TOOL_CALL, {"name": name, **extra})

    def log_error(self, message: str, **extra: Any) -> None:
        self._emit(EventType.ERROR, {"message": message, **extra})

    def _emit(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        event = Event(
            session_id=self.session_id,
            event_type=event_type,
            agent_id=self.agent_id,
            channel=self.channel,
            turn_id=self.turn_id,
            payload=payload,
        )
        self._sink.send(event)


class AgentSession:
    """Traces one end-to-end session for any agent (voice, text, web chat, ...)."""

    def __init__(self, agent_id: str, channel: Channel = Channel.OTHER,
                 session_id: Optional[str] = None,
                 store: Optional[TraceStore] = None,
                 server_url: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.channel = channel if isinstance(channel, Channel) else Channel(channel)
        self.session_id = session_id or new_id("sess")
        self.metadata = metadata or {}
        self._sink = _EventSink(store, server_url)
        self._start_time: Optional[float] = None

    def __enter__(self) -> "AgentSession":
        self._start_time = time.time()
        self._emit(EventType.SESSION_START, {"metadata": self.metadata})
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        status = "error" if exc is not None else "closed"
        if exc is not None:
            self.log_error(str(exc), error_type=exc_type.__name__ if exc_type else "Exception")
        self._emit(EventType.SESSION_END, {"status": status})

    def turn(self, user_input: Optional[str] = None) -> Turn:
        return Turn(self._sink, self.session_id, self.agent_id, self.channel, user_input=user_input)

    def log_llm_call(self, model: str, input_tokens: int, output_tokens: int,
                      latency_ms: Optional[float] = None, **extra: Any) -> None:
        self._emit(EventType.LLM_CALL, {
            "model": model, "input_tokens": input_tokens, "output_tokens": output_tokens,
            "latency_ms": latency_ms, **extra,
        })

    def log_tool_call(self, name: str, **extra: Any) -> None:
        self._emit(EventType.TOOL_CALL, {"name": name, **extra})

    def log_error(self, message: str, **extra: Any) -> None:
        self._emit(EventType.ERROR, {"message": message, **extra})

    def _emit(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        event = Event(
            session_id=self.session_id,
            event_type=event_type,
            agent_id=self.agent_id,
            channel=self.channel,
            payload=payload,
        )
        self._sink.send(event)
