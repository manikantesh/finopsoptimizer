"""
Data models for AgentOps: agent-session tracing, token costs, and alerts.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Channel(str, Enum):
    """Interaction channel the agent session came in on."""
    VOICE = "voice"
    TEXT = "text"
    WEB = "web"
    OTHER = "other"


class EventType(str, Enum):
    """Types of events that can be ingested for a session."""
    SESSION_START = "session_start"
    TURN_START = "turn_start"
    LLM_CALL = "llm_call"
    TOOL_CALL = "tool_call"
    ERROR = "error"
    TURN_END = "turn_end"
    SESSION_END = "session_end"


class AlertSeverity(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class Event:
    """A single ingested event belonging to a session."""
    session_id: str
    event_type: EventType
    agent_id: str = "unknown-agent"
    channel: Channel = Channel.OTHER
    turn_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: new_id("evt"))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        return cls(
            session_id=data["session_id"],
            event_type=EventType(data["event_type"]),
            agent_id=data.get("agent_id", "unknown-agent"),
            channel=Channel(data.get("channel", Channel.OTHER.value)),
            turn_id=data.get("turn_id"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", time.time()),
            event_id=data.get("event_id") or new_id("evt"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "channel": self.channel.value,
            "turn_id": self.turn_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


@dataclass
class Alert:
    alert_id: str
    rule: str
    severity: AlertSeverity
    message: str
    session_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    root_cause: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "rule": self.rule,
            "severity": self.severity.value,
            "message": self.message,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "root_cause": self.root_cause,
        }
