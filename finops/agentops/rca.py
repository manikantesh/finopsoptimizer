"""
Rule-based root-cause analysis for AgentOps.

Deliberately simple (threshold rules over ``TraceStore.window_stats``/
``recent_errors``, no ML) to match the embedded/SQLite "see it work in five
minutes" philosophy of the rest of this package -- swap in something fancier
later without changing the ``Alert`` contract callers already read.
"""

import logging
import time
from collections import Counter
from typing import Dict, List, Optional

from .models import Alert, AlertSeverity, new_id
from .store import TraceStore

logger = logging.getLogger(__name__)


class RootCauseAnalyzer:
    """Periodically checks recent activity for cost/error/latency anomalies."""

    def __init__(
        self,
        store: TraceStore,
        window_seconds: float = 900,
        baseline_seconds: float = 3600,
        cost_spike_multiplier: float = 3.0,
        min_window_cost_usd: float = 0.01,
        error_rate_threshold: float = 0.25,
        min_calls_for_error_rate: int = 5,
        latency_p95_ms_threshold: float = 5000,
        cooldown_seconds: float = 60,
    ):
        self.store = store
        self.window_seconds = window_seconds
        self.baseline_seconds = baseline_seconds
        self.cost_spike_multiplier = cost_spike_multiplier
        self.min_window_cost_usd = min_window_cost_usd
        self.error_rate_threshold = error_rate_threshold
        self.min_calls_for_error_rate = min_calls_for_error_rate
        self.latency_p95_ms_threshold = latency_p95_ms_threshold
        self.cooldown_seconds = cooldown_seconds
        self._last_fired: Dict[str, float] = {}

    def run_once(self) -> List[Alert]:
        """Check current activity against thresholds, inserting any new alerts."""
        stats = self.store.window_stats(self.window_seconds)
        baseline = self.store.window_stats(self.baseline_seconds)
        fired: List[Alert] = []

        cost_alert = self._check_cost_spike(stats, baseline)
        if cost_alert:
            fired.append(cost_alert)

        error_alert = self._check_error_rate(stats)
        if error_alert:
            fired.append(error_alert)

        latency_alert = self._check_latency(stats)
        if latency_alert:
            fired.append(latency_alert)

        for alert in fired:
            self.store.insert_alert(alert)
            logger.info("agentops: alert fired: %s (%s)", alert.rule, alert.severity.value)

        return fired

    def _should_fire(self, rule: str) -> bool:
        last = self._last_fired.get(rule, 0)
        if time.time() - last < self.cooldown_seconds:
            return False
        self._last_fired[rule] = time.time()
        return True

    def _check_cost_spike(self, stats: dict, baseline: dict) -> Optional[Alert]:
        if stats["cost"] < self.min_window_cost_usd:
            return None
        window_rate = stats["cost"] / max(stats["window_seconds"], 1)
        baseline_rate = baseline["cost"] / max(baseline["window_seconds"], 1)
        if baseline_rate <= 0:
            return None
        if window_rate < baseline_rate * self.cost_spike_multiplier:
            return None
        if not self._should_fire("cost_spike"):
            return None
        return Alert(
            alert_id=new_id("alert"),
            rule="cost_spike",
            severity=AlertSeverity.CRITICAL,
            message=(
                f"Spend rate over the last {int(stats['window_seconds'])}s "
                f"(${window_rate:.4f}/s) is {window_rate / baseline_rate:.1f}x "
                f"the trailing baseline (${baseline_rate:.4f}/s)."
            ),
            root_cause=self._dominant_model_root_cause(),
        )

    def _check_error_rate(self, stats: dict) -> Optional[Alert]:
        calls = stats["llm_calls"]
        if calls < self.min_calls_for_error_rate:
            return None
        rate = stats["errors"] / calls
        if rate < self.error_rate_threshold:
            return None
        if not self._should_fire("error_rate_high"):
            return None
        return Alert(
            alert_id=new_id("alert"),
            rule="error_rate_high",
            severity=AlertSeverity.CRITICAL,
            message=(
                f"Error rate over the last {int(stats['window_seconds'])}s is "
                f"{rate:.0%} ({stats['errors']} errors / {calls} calls)."
            ),
            root_cause=self._top_error_message(),
        )

    def _check_latency(self, stats: dict) -> Optional[Alert]:
        p95 = stats["latency_p95_ms"]
        if not p95 or p95 < self.latency_p95_ms_threshold:
            return None
        if not self._should_fire("latency_p95_high"):
            return None
        return Alert(
            alert_id=new_id("alert"),
            rule="latency_p95_high",
            severity=AlertSeverity.WARNING,
            message=(
                f"P95 LLM-call latency over the last {int(stats['window_seconds'])}s "
                f"is {p95:.0f}ms (threshold {self.latency_p95_ms_threshold:.0f}ms)."
            ),
        )

    def _top_error_message(self) -> Optional[str]:
        messages = self.store.recent_error_messages(self.window_seconds, limit=50)
        if not messages:
            return None
        top, count = Counter(messages).most_common(1)[0]
        return f"Most common error ({count}x): {top}"

    def _dominant_model_root_cause(self) -> Optional[str]:
        models = self.store.recent_llm_models(self.window_seconds, limit=200)
        if not models:
            return None
        top, count = Counter(models).most_common(1)[0]
        return f"Dominant model in window: {top} ({count} calls)"
