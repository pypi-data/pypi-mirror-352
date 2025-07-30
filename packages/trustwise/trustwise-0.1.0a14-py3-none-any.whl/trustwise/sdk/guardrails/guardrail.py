import warnings
from collections.abc import Callable
from typing import Any

import requests

from trustwise.sdk.features import is_beta_feature
from trustwise.sdk.protocols import TrustwiseClientProtocol
from trustwise.sdk.types import GuardrailResponse


class Guardrail:
    """
    Guardrail system for Trustwise API responses.
    
    .. warning::
        This feature is currently in beta. The API and functionality may change in future releases.
    """

    def __init__(
        self,
        trustwise_client: TrustwiseClientProtocol,
        thresholds: dict[str, float],
        *, # This is a marker to indicate that the following arguments are keyword-only
        block_on_failure: bool = False,
        callbacks: dict[str, Callable] | None = None
    ) -> None:
        """
        Initialize the guardrail system.

        Args:
            trustwise_client: The Trustwise client instance.
            thresholds: Dictionary of metric names and their threshold values (0-100).
            block_on_failure: Whether to block responses that fail any metric.
            callbacks: Optional callbacks for metric evaluation results.

        Raises:
            ValueError: If thresholds are invalid.
        """
        if is_beta_feature("guardrails"):
            warnings.warn(
                "The guardrails feature is currently in beta. The API and functionality may change in future releases.",
                UserWarning,
                stacklevel=2
            )
            
        # Validate thresholds
        if not thresholds:
            raise ValueError("Thresholds dictionary cannot be empty")
        
        for metric, threshold in thresholds.items():
            if not isinstance(threshold, int | float) or isinstance(threshold, bool):
                raise ValueError(f"Threshold for {metric} must be a number")
            if not 0 <= threshold <= 100:
                raise ValueError(f"Threshold for {metric} must be between 0 and 100")

        self.client = trustwise_client
        self.thresholds = thresholds
        self.block_on_failure = block_on_failure
        self.callbacks = callbacks or {}
        self.evaluation_results = {}

    def evaluate(
        self,
        query: str,
        response: str,
        context: list[dict[str, Any]] | dict[str, Any] | None = None
    ) -> GuardrailResponse:
        """Evaluate a response against configured metrics."""
        if not query or not response:
            raise ValueError("Query and response are required parameters")
        
        if context is not None and not isinstance(context, list | dict):
            raise ValueError("Context must be a list or dictionary")
            
        results = {}
        passed = True
        blocked = False
        
        for metric, threshold in self.thresholds.items():
            try:
                if metric == "faithfulness":
                    result = self.client.metrics.faithfulness.evaluate(
                        query=query,
                        response=response,
                        context=context
                    )
                    score = result.score
                elif metric == "answer_relevancy":
                    result = self.client.metrics.answer_relevancy.evaluate(
                        query=query,
                        response=response,
                        context=context
                    )
                    score = result.score
                elif metric == "context_relevancy":
                    result = self.client.metrics.context_relevancy.evaluate(
                        query=query,
                        response=response,
                        context=context
                    )
                    score = result.score
                elif metric in ["clarity", "helpfulness", "formality", "simplicity"]:
                    # Alignment metrics
                    result = getattr(self.client.metrics, metric).evaluate(
                        query=query,
                        response=response
                    )
                    score = result.score
                elif metric == "toxicity":
                    # Toxicity metric
                    result = self.client.metrics.toxicity.evaluate(
                        query=query,
                        response=response
                    )
                    score = max(result.scores)  # Use maximum toxicity score
                elif metric == "prompt_injection":
                    # Prompt injection metric
                    result = self.client.metrics.prompt_injection.evaluate(
                        query=query,
                        response=response,
                        context=context
                    )
                    score = result.score
                else:
                    raise ValueError(f"Unknown metric: {metric}")
                
                results[metric] = {
                    "passed": score >= threshold,
                    "result": result
                }
                
                if metric in self.callbacks:
                    self.callbacks[metric](metric, result)

                if not results[metric]["passed"]:
                    passed = False
                    if self.block_on_failure:
                        blocked = True
                        break
                        
            except (ValueError, AttributeError, KeyError, requests.exceptions.RequestException) as e:
                results[metric] = {
                    "passed": False,
                    "result": {"score": 0.0},
                    "error": str(e)
                }
                passed = False
                if self.block_on_failure:
                    blocked = True
                    break
        
        return GuardrailResponse(
            passed=passed,
            blocked=blocked,
            results=results
        )

    def check_pii(
        self,
        text: str,
        allowlist: list[str] | None = None,
        blocklist: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Check text for PII and determine if it should be blocked.
        
        Args:
            text: Text to check for PII
            allowlist: Optional list of allowed terms
            blocklist: Optional list of blocked terms
            
        Returns:
            Dictionary with PII detection results and pass/fail status
        """
        try:
            result = self.client.metrics.pii.evaluate(
                text=text,
                allowlist=allowlist,
                blocklist=blocklist
            )
            
            # Consider it passed if no PII is found or only allowlisted items are found
            has_pii = len(result.get("identified_pii", [])) > 0
            
            return {
                "passed": not has_pii,
                "result": result,
                "blocked": self.block_on_failure and has_pii
            }
        except (ValueError, AttributeError, KeyError, requests.exceptions.RequestException) as e:
            return {
                "passed": not self.block_on_failure,
                "error": str(e),
                "blocked": self.block_on_failure
            } 