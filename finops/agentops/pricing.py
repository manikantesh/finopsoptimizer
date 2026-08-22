"""
Token pricing for AgentOps: turns (model, input_tokens, output_tokens) into a dollar cost.

Prices drift constantly and vary by contract/region, so the defaults below are a
reasonable starting point, not a guarantee -- override them via ``agentops.pricing_overrides``
in the YAML config (see docs/agent-observability.md) or by passing ``overrides`` directly.
"""

from typing import Dict, Optional

# Default $ per 1,000,000 tokens (input, output). Update these to match your actual
# contracted rates -- see docs/agent-observability.md#pricing for how to override.
DEFAULT_MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # Anthropic Claude
    "claude-opus-5": {"input": 15.00, "output": 75.00},
    "claude-sonnet-5": {"input": 3.00, "output": 15.00},
    "claude-fable-5": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 0.80, "output": 4.00},
    # OpenAI
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    # Google Gemini
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    # Fallback used when a model isn't in the table at all.
    "unknown": {"input": 1.00, "output": 3.00},
}


class TokenPricingCalculator:
    """Computes the dollar cost of an LLM call from its token counts."""

    def __init__(self, overrides: Optional[Dict[str, Dict[str, float]]] = None):
        self.rates: Dict[str, Dict[str, float]] = {
            **DEFAULT_MODEL_PRICING,
            **(overrides or {}),
        }

    def rate_for(self, model: str) -> Dict[str, float]:
        return self.rates.get(model, self.rates["unknown"])

    def cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Return the dollar cost of a single LLM call."""
        rate = self.rate_for(model)
        return (input_tokens / 1_000_000) * rate["input"] + (output_tokens / 1_000_000) * rate["output"]

    def price_table(self) -> Dict[str, Dict[str, float]]:
        return dict(self.rates)
