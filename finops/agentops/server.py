"""
FastAPI app for AgentOps: OTLP ingestion API + read API + the live "ops wall".

The ingestion endpoint (``POST /v1/traces``) accepts standard OpenTelemetry
traces (OTLP/HTTP JSON) -- this is the *only* ingestion contract, by design,
so any agent in any language/runtime that can export OTel traces works here
with zero custom SDK. Python agents can alternatively use the
``AgentSession``/``Turn`` convenience wrapper in ``finops.agentops.tracer``,
which either writes straight to an embedded store or emits the same OTLP
shape to this endpoint remotely. See docs/agent-observability.md.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from .otlp import parse_otlp_traces
from .paths import DEFAULT_ALERT_INTERVAL_SECONDS
from .rca import RootCauseAnalyzer
from .store import TraceStore

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


def create_app(
    store: TraceStore,
    rca: Optional[RootCauseAnalyzer] = None,
    alert_interval_seconds: float = DEFAULT_ALERT_INTERVAL_SECONDS,
):
    """Build the FastAPI application. Import is deferred so ``fastapi`` stays optional."""
    try:
        from fastapi import FastAPI, HTTPException, Request
        from fastapi.responses import HTMLResponse, StreamingResponse
    except ImportError as exc:  # pragma: no cover - exercised via CLI hint, not tests
        raise ImportError(
            "The agentops server needs the optional 'agentops' extra: "
            "pip install -e '.[agentops]'  (or -r requirements-agentops.txt)"
        ) from exc

    rca = rca or RootCauseAnalyzer(store)

    async def _alert_loop() -> None:
        while True:
            await asyncio.sleep(alert_interval_seconds)
            try:
                rca.run_once()
            except Exception:  # background loop must never take the server down
                logger.exception("agentops: alert check failed")

    @asynccontextmanager
    async def lifespan(app: "FastAPI"):
        task = asyncio.create_task(_alert_loop())
        try:
            yield
        finally:
            task.cancel()

    app = FastAPI(
        title="FinOps AgentOps",
        description="Live ops wall for AI agent sessions & cost",
        lifespan=lifespan,
    )
    app.state.store = store
    app.state.rca = rca

    @app.get("/", response_class=HTMLResponse)
    async def dashboard() -> str:
        return (STATIC_DIR / "dashboard.html").read_text()

    @app.post("/v1/traces")
    async def ingest_traces(request: Request) -> Dict[str, Any]:
        try:
            body = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail=f"invalid JSON: {exc}") from exc
        try:
            events = parse_otlp_traces(body)
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=f"invalid OTLP payload: {exc}") from exc
        costs = [store.record_event(event) for event in events]
        return {"ok": True, "spans_received": len(events), "cost": sum(c or 0 for c in costs)}

    @app.get("/api/sessions")
    async def sessions(limit: int = 50):
        return store.list_sessions(limit=limit)

    @app.get("/api/sessions/{session_id}")
    async def session_detail(session_id: str):
        session = store.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="session not found")
        return session

    @app.get("/api/alerts")
    async def alerts(limit: int = 50):
        return store.list_alerts(limit=limit)

    @app.get("/api/stats")
    async def stats(window_seconds: float = 3600):
        return store.window_stats(window_seconds)

    @app.get("/api/live")
    async def live(request: Request):
        async def event_stream():
            while True:
                if await request.is_disconnected():
                    break
                payload = {
                    "sessions": store.list_sessions(limit=20),
                    "alerts": store.list_alerts(limit=10),
                    "stats": store.window_stats(3600),
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(2)

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return app
