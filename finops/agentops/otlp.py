"""
OTLP/HTTP JSON parsing -- the *only* ingestion contract AgentOps accepts.

Any agent, in any language, that can export standard OpenTelemetry traces can
feed this system: point an OTLP/HTTP exporter at ``POST /v1/traces``. This
module reads the JSON encoding of ``ExportTraceServiceRequest`` (the same
field names as the OTLP protobuf, since OTLP/HTTP supports plain JSON) --
no ``opentelemetry-proto`` dependency needed.

It looks for the GenAI semantic-convention attributes
(https://opentelemetry.io/docs/specs/semconv/gen-ai/) on each span:

- ``gen_ai.system``                 -> provider (e.g. "anthropic", "openai")
- ``gen_ai.request.model`` /
  ``gen_ai.response.model``         -> model name
- ``gen_ai.usage.input_tokens`` /
  ``gen_ai.usage.output_tokens``    -> token counts (cost is computed from these)
- ``gen_ai.tool.name``              -> tool-call spans
- ``session.id`` / ``turn.id``      -> AgentOps session/turn grouping (recommended;
                                        falls back to the span's traceId/parentSpanId
                                        if omitted, so plain OTel traces still work)
- ``gen_ai.agent.name`` / resource ``service.name`` -> agent identity
- span ``status.code == STATUS_CODE_ERROR`` -> also recorded as an error event

See docs/agent-observability.md for the full attribute reference and examples.
"""

import time
from typing import Any, Dict, List, Optional

from .models import Channel, Event, EventType

_STATUS_CODE_ERROR = 2
_STATUS_CODE_UNSET = 0


def parse_otlp_traces(payload: Dict[str, Any]) -> List[Event]:
    """Convert an OTLP/HTTP JSON ``ExportTraceServiceRequest`` body into Events."""
    events: List[Event] = []
    for resource_span in payload.get("resourceSpans", []) or []:
        resource_attrs = _attrs_to_dict(resource_span.get("resource", {}).get("attributes", []))
        for scope_span in resource_span.get("scopeSpans", []) or []:
            for span in scope_span.get("spans", []) or []:
                events.extend(_span_to_events(span, resource_attrs))
    return events


def _span_to_events(span: Dict[str, Any], resource_attrs: Dict[str, Any]) -> List[Event]:
    attrs = {**resource_attrs, **_attrs_to_dict(span.get("attributes", []))}

    session_id = attrs.get("session.id") or span.get("traceId") or "unknown-session"
    turn_id = attrs.get("turn.id") or span.get("parentSpanId") or span.get("spanId")
    agent_id = attrs.get("gen_ai.agent.name") or resource_attrs.get("service.name") or "unknown-agent"
    channel = _parse_channel(attrs.get("finops.channel"))

    start_ns = _to_int(span.get("startTimeUnixNano"))
    end_ns = _to_int(span.get("endTimeUnixNano"))
    base: Dict[str, Any] = dict(session_id=session_id, agent_id=agent_id, channel=channel, turn_id=turn_id)
    if end_ns:
        base["timestamp"] = end_ns / 1e9
    latency_ms = (end_ns - start_ns) / 1e6 if start_ns and end_ns else None

    events: List[Event] = []
    is_llm_call = any(k.startswith("gen_ai.") for k in attrs) and not attrs.get("gen_ai.tool.name")

    if is_llm_call:
        events.append(Event(
            event_type=EventType.LLM_CALL,
            payload={
                "model": attrs.get("gen_ai.response.model") or attrs.get("gen_ai.request.model") or "unknown",
                "provider": attrs.get("gen_ai.system"),
                "input_tokens": _to_int(attrs.get("gen_ai.usage.input_tokens")) or 0,
                "output_tokens": _to_int(attrs.get("gen_ai.usage.output_tokens")) or 0,
                "latency_ms": latency_ms,
            },
            **base,
        ))
    elif attrs.get("gen_ai.tool.name") or attrs.get("tool.name"):
        events.append(Event(
            event_type=EventType.TOOL_CALL,
            payload={"name": attrs.get("gen_ai.tool.name") or attrs.get("tool.name")},
            **base,
        ))

    status = span.get("status") or {}
    if status.get("code") == _STATUS_CODE_ERROR:
        events.append(Event(
            event_type=EventType.ERROR,
            payload={
                "message": status.get("message") or "span reported an error",
                "error_type": "SpanError",
            },
            **base,
        ))

    return events


def event_to_otlp_payload(event: Event) -> Optional[Dict[str, Any]]:
    """Build a single-span OTLP/HTTP JSON export request from an internal Event.

    Used by the SDK's remote mode so that even Python callers of ``AgentSession``
    speak the same OTLP-only wire contract as any other language would. Returns
    ``None`` for event types this endpoint can't do anything with (session/turn
    lifecycle markers), so the caller can skip the request entirely.
    """
    attrs: List[Dict[str, Any]] = [
        {"key": "session.id", "value": {"stringValue": event.session_id}},
    ]
    if event.turn_id:
        attrs.append({"key": "turn.id", "value": {"stringValue": event.turn_id}})
    attrs.append({"key": "finops.channel", "value": {"stringValue": event.channel.value}})

    status: Dict[str, Any] = {"code": _STATUS_CODE_UNSET}

    if event.event_type == EventType.LLM_CALL:
        p = event.payload
        attrs.extend([
            {"key": "gen_ai.system", "value": {"stringValue": p.get("provider") or ""}},
            {"key": "gen_ai.request.model", "value": {"stringValue": p.get("model", "unknown")}},
            {"key": "gen_ai.usage.input_tokens", "value": {"intValue": str(p.get("input_tokens", 0))}},
            {"key": "gen_ai.usage.output_tokens", "value": {"intValue": str(p.get("output_tokens", 0))}},
        ])
        latency_ms = p.get("latency_ms") or 0
    elif event.event_type == EventType.TOOL_CALL:
        attrs.append({"key": "gen_ai.tool.name", "value": {"stringValue": event.payload.get("name", "")}})
        latency_ms = 0
    elif event.event_type == EventType.ERROR:
        status = {"code": _STATUS_CODE_ERROR, "message": event.payload.get("message", "")}
        latency_ms = 0
    else:
        return None  # session/turn lifecycle markers: nothing for this endpoint to do

    end_ns = int(event.timestamp * 1e9)
    start_ns = end_ns - int(max(latency_ms, 0) * 1e6)

    return {
        "resourceSpans": [{
            "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": event.agent_id}}]},
            "scopeSpans": [{
                "scope": {"name": "finops.agentops.tracer"},
                "spans": [{
                    "traceId": event.session_id,
                    "spanId": event.event_id,
                    "parentSpanId": event.turn_id or "",
                    "name": event.event_type.value,
                    "startTimeUnixNano": str(start_ns),
                    "endTimeUnixNano": str(end_ns),
                    "attributes": attrs,
                    "status": status,
                }],
            }],
        }],
    }


def _attr_value(value: Dict[str, Any]) -> Any:
    if "stringValue" in value:
        return value["stringValue"]
    if "intValue" in value:
        return _to_int(value["intValue"])
    if "doubleValue" in value:
        return value["doubleValue"]
    if "boolValue" in value:
        return value["boolValue"]
    if "arrayValue" in value:
        return [_attr_value(v) for v in value["arrayValue"].get("values", [])]
    return None


def _attrs_to_dict(attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {attr["key"]: _attr_value(attr.get("value", {})) for attr in attributes or []}


def _parse_channel(value: Optional[str]) -> Channel:
    if not value:
        return Channel.OTHER
    try:
        return Channel(value)
    except ValueError:
        return Channel.OTHER


def _to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
