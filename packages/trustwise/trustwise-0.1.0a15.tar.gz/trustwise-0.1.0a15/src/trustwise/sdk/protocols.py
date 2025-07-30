from typing import Any, Protocol


class MetricProtocol(Protocol):
    """Protocol for metric evaluation interface."""
    def evaluate(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """Evaluate the metric with given parameters."""
        ...

    def batch_evaluate(self, **kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        """Evaluate multiple inputs in a single request."""
        ...

    def explain(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """Get detailed explanation of the evaluation."""
        ...


class TrustwiseClientProtocol(Protocol):
    """Protocol for Trustwise client interface."""
    safety: Any
    alignment: Any
    performance: Any
    guardrails: Any 