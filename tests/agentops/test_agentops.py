"""Smoke tests for the AgentOps package: SDK, OTLP parsing, server, and RCA.

Run with: cd finopsoptimizer && python -m pytest tests/agentops -v
Needs the 'agentops' extra (fastapi) installed -- these tests are skipped otherwise.
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from finops.agentops import AgentSession, RootCauseAnalyzer, TraceStore
from finops.agentops.otlp import event_to_otlp_payload, parse_otlp_traces
from finops.agentops.models import Channel, Event, EventType

fastapi = pytest.importorskip("fastapi")


@pytest.fixture
def store():
    path = tempfile.mktemp(suffix=".db")
    s = TraceStore(path)
    yield s
    s.close()
    os.remove(path)


@pytest.fixture
def client(store):
    from fastapi.testclient import TestClient

    from finops.agentops.server import create_app

    app = create_app(store, alert_interval_seconds=10_000)  # don't fire the background loop mid-test
    return TestClient(app)


def test_embedded_sdk_writes_session_and_cost(store):
    with AgentSession(agent_id="test-agent", channel="voice", store=store) as session:
        with session.turn(user_input="hi") as turn:
            turn.log_llm_call(model="claude-sonnet-5", input_tokens=1_000_000, output_tokens=1_000_000, latency_ms=300)
            turn.log_tool_call(name="lookup", ok=True)

    sessions = store.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["agent_id"] == "test-agent"
    assert sessions[0]["status"] == "closed"
    assert sessions[0]["call_count"] == 1
    assert sessions[0]["total_cost"] == pytest.approx(3.00 + 15.00)  # claude-sonnet-5 default rate


def test_embedded_sdk_records_error_and_marks_session(store):
    with AgentSession(agent_id="test-agent", store=store) as session:
        with session.turn() as turn:
            turn.log_error("boom", error_type="Boom")

    sessions = store.list_sessions()
    assert sessions[0]["status"] == "error"
    assert sessions[0]["error_count"] == 1


def test_otlp_parses_gen_ai_span_into_llm_call_event():
    payload = {
        "resourceSpans": [{
            "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "otel-agent"}}]},
            "scopeSpans": [{
                "spans": [{
                    "traceId": "trace-1",
                    "spanId": "span-1",
                    "startTimeUnixNano": "1700000000000000000",
                    "endTimeUnixNano": "1700000000500000000",
                    "attributes": [
                        {"key": "session.id", "value": {"stringValue": "sess-1"}},
                        {"key": "gen_ai.system", "value": {"stringValue": "openai"}},
                        {"key": "gen_ai.request.model", "value": {"stringValue": "gpt-4o-mini"}},
                        {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "200"}},
                        {"key": "gen_ai.usage.output_tokens", "value": {"intValue": "80"}},
                    ],
                    "status": {"code": 0},
                }],
            }],
        }],
    }
    events = parse_otlp_traces(payload)
    assert len(events) == 1
    e = events[0]
    assert e.event_type == EventType.LLM_CALL
    assert e.session_id == "sess-1"
    assert e.agent_id == "otel-agent"
    assert e.payload["model"] == "gpt-4o-mini"
    assert e.payload["input_tokens"] == 200
    assert e.payload["latency_ms"] == pytest.approx(500)


def test_otlp_error_status_produces_error_event():
    payload = {
        "resourceSpans": [{
            "resource": {"attributes": []},
            "scopeSpans": [{"spans": [{
                "traceId": "trace-2", "spanId": "span-2",
                "attributes": [{"key": "session.id", "value": {"stringValue": "sess-2"}}],
                "status": {"code": 2, "message": "timeout"},
            }]}],
        }],
    }
    events = parse_otlp_traces(payload)
    assert len(events) == 1
    assert events[0].event_type == EventType.ERROR
    assert events[0].payload["message"] == "timeout"


def test_event_to_otlp_round_trips_llm_call():
    event = Event(
        session_id="sess-3", event_type=EventType.LLM_CALL, agent_id="rt-agent",
        channel=Channel.TEXT, turn_id="turn-1",
        payload={"model": "claude-sonnet-5", "provider": "anthropic", "input_tokens": 10, "output_tokens": 5, "latency_ms": 120},
    )
    otlp_payload = event_to_otlp_payload(event)
    assert otlp_payload is not None
    parsed = parse_otlp_traces(otlp_payload)
    assert len(parsed) == 1
    assert parsed[0].session_id == "sess-3"
    assert parsed[0].agent_id == "rt-agent"
    assert parsed[0].payload["model"] == "claude-sonnet-5"
    assert parsed[0].payload["input_tokens"] == 10


def test_event_to_otlp_skips_lifecycle_markers():
    event = Event(session_id="sess-4", event_type=EventType.SESSION_START, agent_id="a")
    assert event_to_otlp_payload(event) is None


def test_server_ingests_otlp_traces_and_lists_sessions(client):
    import time as _time
    end_ns = int(_time.time() * 1e9)
    start_ns = end_ns - int(0.5 * 1e9)
    payload = {
        "resourceSpans": [{
            "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "curl-agent"}}]},
            "scopeSpans": [{"spans": [{
                "traceId": "curl-session-1", "spanId": "span-1",
                "startTimeUnixNano": str(start_ns),
                "endTimeUnixNano": str(end_ns),
                "attributes": [
                    {"key": "session.id", "value": {"stringValue": "curl-session-1"}},
                    {"key": "gen_ai.system", "value": {"stringValue": "openai"}},
                    {"key": "gen_ai.request.model", "value": {"stringValue": "gpt-4o-mini"}},
                    {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "200"}},
                    {"key": "gen_ai.usage.output_tokens", "value": {"intValue": "80"}},
                ],
                "status": {"code": 0},
            }]}],
        }],
    }
    resp = client.post("/v1/traces", json=payload)
    assert resp.status_code == 200
    assert resp.json()["spans_received"] == 1

    sessions = client.get("/api/sessions").json()
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == "curl-session-1"

    stats = client.get("/api/stats").json()
    assert stats["llm_calls"] == 1


def test_server_rejects_malformed_json(client):
    resp = client.post("/v1/traces", content=b"not json", headers={"content-type": "application/json"})
    assert resp.status_code == 422


def test_dashboard_route_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AgentOps" in resp.text


def test_rca_fires_error_rate_alert(store):
    for i in range(10):
        with AgentSession(agent_id="flaky-agent", store=store) as session:
            with session.turn() as turn:
                turn.log_llm_call(model="claude-sonnet-5", input_tokens=10, output_tokens=10, latency_ms=100)
                if i < 5:
                    turn.log_error("tool timeout", error_type="ToolTimeout")

    rca = RootCauseAnalyzer(store, min_calls_for_error_rate=5)
    alerts = rca.run_once()
    rules = {a.rule for a in alerts}
    assert "error_rate_high" in rules
    error_alert = next(a for a in alerts if a.rule == "error_rate_high")
    assert error_alert.root_cause and "tool timeout" in error_alert.root_cause


def test_rca_cooldown_prevents_duplicate_alerts(store):
    for i in range(10):
        with AgentSession(agent_id="flaky-agent", store=store) as session:
            with session.turn() as turn:
                turn.log_llm_call(model="claude-sonnet-5", input_tokens=10, output_tokens=10, latency_ms=100)
                turn.log_error("boom")

    rca = RootCauseAnalyzer(store, min_calls_for_error_rate=5, cooldown_seconds=9999)
    first = rca.run_once()
    second = rca.run_once()
    assert len(first) >= 1
    assert len(second) == 0
