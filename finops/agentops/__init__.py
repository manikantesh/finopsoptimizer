"""
AgentOps: lightweight agent-session tracing, token cost, and alerting.

Embeds into any Python agent (``AgentSession``/``Turn``) or accepts standard
OpenTelemetry traces over HTTP from any language (``POST /v1/traces``) --
see docs/agent-observability.md. No external database required: everything
is backed by a single SQLite file.
"""

from .models import Alert, AlertSeverity, Channel, Event, EventType
from .paths import DEFAULT_ALERT_INTERVAL_SECONDS, DEFAULT_DB_PATH, DEFAULT_HOST, DEFAULT_PORT
from .pricing import TokenPricingCalculator
from .rca import RootCauseAnalyzer
from .store import TraceStore
from .tracer import AgentSession, Turn

__all__ = [
    "AgentSession",
    "Turn",
    "Channel",
    "EventType",
    "Event",
    "Alert",
    "AlertSeverity",
    "TraceStore",
    "TokenPricingCalculator",
    "RootCauseAnalyzer",
    "DEFAULT_DB_PATH",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DEFAULT_ALERT_INTERVAL_SECONDS",
]
