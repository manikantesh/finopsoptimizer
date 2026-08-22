# Agent Observability (AgentOps)

AgentOps traces AI agent sessions, computes per-call token cost, and raises
root-cause alerts for cost/error/latency anomalies -- all from a single
`pip install`, with **no external database, message queue, or Docker
required**. It ships inside this same `finopsoptimizer` package, as a
lightweight companion to the multi-cloud infrastructure-cost tooling.

- **Ingestion is OpenTelemetry-only.** Any agent, in any language, that can
  export standard OTLP traces works here -- there is no proprietary SDK
  format to adopt.
- **Storage is one SQLite file.** No ClickHouse/Postgres/Kafka to run.
- **The dashboard is a static HTML page** served by the same process,
  live-updated over server-sent events.

## Quick start (2 minutes)

```bash
git clone https://github.com/manikantesh/finopsoptimizer.git
cd finopsoptimizer
pip install -e '.[agentops]'          # fastapi + uvicorn + requests only

finops agentops demo                  # writes a few sample sessions locally
finops agentops serve                 # http://127.0.0.1:8787
```

Open `http://127.0.0.1:8787/` and you'll see the demo sessions, their cost,
and (since one demo turn is seeded to fail) a live alert. `finops agentops
serve --help` / `finops agentops demo --help` show all options
(`--host`, `--port`, `--db-path`).

Nothing here touches your cloud credentials or the multi-cloud cost modules
-- `finops agentops` only needs `fastapi`/`uvicorn`/`requests`, not
`pandas`/`boto3`/`azure-mgmt-*`/`google-cloud-*`.

## Connecting your own agent

### Option A -- instrument with the OpenTelemetry SDK (any language)

This is the recommended path for anything beyond a quick local check: point
a standard OTLP/HTTP exporter at AgentOps and set a handful of
[GenAI semantic-convention](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
attributes on each LLM-call span.

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider(resource=Resource.create({"service.name": "support-agent"}))
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:8787/v1/traces"))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("support-agent")

with tracer.start_as_current_span("chat") as span:
    span.set_attribute("session.id", session_id)     # groups spans into one AgentOps session
    span.set_attribute("gen_ai.system", "anthropic")
    span.set_attribute("gen_ai.request.model", "claude-sonnet-5")
    span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
    span.set_attribute("gen_ai.usage.output_tokens", output_tokens)
    # ... call the model ...
```

`pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-http` (or
whatever your language's OTel SDK + OTLP/HTTP exporter package is called --
this works from Go, Node, Java, Ruby, etc. exactly the same way, since the
wire format is language-neutral).

If you're already using an OTel auto-instrumentation library for your LLM
provider (e.g. one that emits `gen_ai.*` attributes automatically), you
don't need to set those attributes by hand -- just point its OTLP exporter
at `/v1/traces`.

### Option B -- the Python convenience wrapper

For a quick local integration without touching OTel SDK setup directly:

```python
from finops.agentops import AgentSession

with AgentSession(agent_id="support-agent", channel="voice") as session:
    with session.turn(user_input="what's my balance?") as turn:
        turn.log_tool_call(name="lookup_balance", ok=True)
        turn.log_llm_call(
            model="claude-sonnet-5",
            input_tokens=180,
            output_tokens=64,
            latency_ms=420,
        )
```

By default this writes straight to an embedded `TraceStore` (no server
needed at all -- good for a single process / a Jupyter notebook / a test
run). Pass `server_url="http://host:8787"` instead to have it emit the same
OTLP shape to a remote `finops agentops serve` instance:

```python
with AgentSession(agent_id="support-agent", server_url="http://collector:8787") as session:
    ...
```

Under the hood this SDK is just a thin convenience layer -- it builds the
identical OTLP/HTTP payload described in Option A and posts it to `/v1/traces`,
so both integration paths produce the same data.

### Option C -- raw HTTP (no SDK at all)

`POST /v1/traces` accepts the standard OTLP/HTTP JSON encoding directly (the
JSON mapping of `ExportTraceServiceRequest` -- no protobuf/gRPC required):

```bash
curl -X POST http://localhost:8787/v1/traces \
  -H 'Content-Type: application/json' \
  -d '{
    "resourceSpans": [{
      "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "my-agent"}}]},
      "scopeSpans": [{
        "spans": [{
          "traceId": "a1b2c3", "spanId": "d4e5f6",
          "startTimeUnixNano": "1730000000000000000",
          "endTimeUnixNano": "1730000000420000000",
          "attributes": [
            {"key": "session.id", "value": {"stringValue": "sess-42"}},
            {"key": "gen_ai.system", "value": {"stringValue": "openai"}},
            {"key": "gen_ai.request.model", "value": {"stringValue": "gpt-4o-mini"}},
            {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "180"}},
            {"key": "gen_ai.usage.output_tokens", "value": {"intValue": "64"}}
          ],
          "status": {"code": 0}
        }]
      }]
    }]
  }'
```

## Attribute reference

These are the span attributes AgentOps reads. Everything else on the span is
ignored (harmlessly) -- it does not need to be a pure GenAI span.

| Attribute | Required | Meaning |
|---|---|---|
| `session.id` | recommended | Groups spans into one AgentOps session. Falls back to the span's `traceId` if omitted, so plain OTel traces still work, just grouped one-session-per-trace. |
| `turn.id` | optional | Groups spans into one conversational turn. Falls back to `parentSpanId`. |
| `gen_ai.system` | for cost | Provider id (`anthropic`, `openai`, `gemini`, ...). |
| `gen_ai.request.model` / `gen_ai.response.model` | for cost | Model name -- drives the token-pricing lookup (see [Pricing](#pricing) below). |
| `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens` | for cost | Token counts. Without these, the span is still recorded but priced as zero. |
| `gen_ai.agent.name` | optional | Agent identity. Falls back to the resource's `service.name`. |
| `gen_ai.tool.name` (or `tool.name`) | for tool spans | Marks the span as a tool call instead of an LLM call. |
| `finops.channel` | optional | One of `voice` / `text` / `web` / `other` (default `other`). |
| span `status.code == ERROR` | optional | Recorded as an AgentOps error event (drives error-rate alerting) with `status.message` as the error text. |

**Known limitation:** trace/span IDs are treated as opaque grouping
strings, not validated against the strict 32/16-lowercase-hex-char OTLP
spec. If you chain AgentOps behind a stricter OTel Collector pipeline, put
it as the terminal receiver rather than a mid-pipeline passthrough.

## Pricing

Token cost is computed from a built-in default price table
(`finops.agentops.pricing.DEFAULT_MODEL_PRICING`, $ per 1M tokens) covering
current Claude, GPT, and Gemini models, plus an `"unknown"` fallback rate
for anything not in the table. Prices drift and vary by contract -- override
them to match your actual rates:

```python
from finops.agentops import TraceStore
from finops.agentops.pricing import TokenPricingCalculator

pricing = TokenPricingCalculator(overrides={
    "claude-sonnet-5": {"input": 2.50, "output": 12.00},  # your negotiated rate
})
store = TraceStore("agentops_data/agentops.db", pricing=pricing)
```

Pass that `store` into `finops.agentops.server.create_app(store)` if you're
embedding the server yourself instead of using `finops agentops serve`.

## Reading the data back

| Endpoint | Purpose |
|---|---|
| `GET /` | The live dashboard (this is a plain static page + SSE, no build step). |
| `GET /api/sessions?limit=50` | Recent sessions with rollup cost/call/error counts. |
| `GET /api/sessions/{session_id}` | One session's full event timeline. |
| `GET /api/alerts?limit=50` | Root-cause alerts fired so far. |
| `GET /api/stats?window_seconds=3600` | Rollup cost/calls/errors/P95 latency over a trailing window. |
| `GET /api/live` | Server-sent-events stream powering the dashboard; poll this yourself for a custom integration. |

## Alerts & root-cause analysis

A background loop (every `DEFAULT_ALERT_INTERVAL_SECONDS`, 15s) runs
`finops.agentops.rca.RootCauseAnalyzer.run_once()`, which checks the
trailing window against three rule-based thresholds:

- **`cost_spike`** -- spend rate over the window is >= 3x the trailing
  1-hour baseline rate (and above a minimum absolute $ floor, so a single
  cheap call right after startup doesn't trip it).
- **`error_rate_high`** -- error rate over the window is >= 25% with at
  least 5 calls; the alert's `root_cause` is the most common recent error
  message.
- **`latency_p95_high`** -- P95 LLM-call latency over the window exceeds a
  threshold (default 5000ms).

Each rule has its own cooldown (default 60s) so a persistent condition
fires once, not every loop tick. All thresholds are constructor arguments on
`RootCauseAnalyzer` if the defaults don't fit your traffic volume.

## What this is (and isn't)

This is a **local/self-hosted, single-node** tool: one SQLite file, one
process, meant to be `pip install`-ed and run by an engineer evaluating
their own agent, or embedded in a small deployment. It intentionally does
not include a distributed backend (ClickHouse/Kafka/Redis), multi-tenant
auth, or a dashboard builder -- if you need those, see
`docs/future-roadmap.md` for what's tracked as a later milestone versus
what's deliberately out of scope for this lightweight module.
