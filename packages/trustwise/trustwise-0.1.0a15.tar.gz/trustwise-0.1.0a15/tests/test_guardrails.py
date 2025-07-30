from typing import Any
from unittest.mock import patch

import pytest

from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.guardrails.guardrail import Guardrail
from trustwise.sdk.types import GuardrailResponse

from .helpers import get_mock_response


class TestGuardrail:
    """Test suite for Guardrail class."""

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_guardrail_initialization(self, mock_post, sdk):
        """Test guardrail initialization."""
        guardrail = Guardrail(
            trustwise_client=sdk,
            thresholds={"faithfulness": 80, "clarity": 70}
        )
        assert isinstance(guardrail, Guardrail)
        assert hasattr(guardrail, "client")
        assert guardrail.thresholds["faithfulness"] == 80
        assert guardrail.thresholds["clarity"] == 70
        assert guardrail.block_on_failure is False

    @patch("trustwise.sdk.metrics.v3.metrics.faithfulness.FaithfulnessMetric.evaluate")
    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_evaluate(
        self,
        mock_post: Any,
        mock_faithfulness_evaluate: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list,
        sample_response: str
    ) -> None:
        """Test response evaluation with default metrics."""
        mock_post.return_value = get_mock_response("guardrails/evaluate")
        mock_faithfulness_evaluate.return_value = get_mock_response("safety/faithfulness")
        guardrail = Guardrail(
            trustwise_client=sdk,
            thresholds={"faithfulness": 80, "clarity": 70}
        )
        result = guardrail.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        
        assert isinstance(result, GuardrailResponse)
        assert isinstance(result.passed, bool)
        assert isinstance(result.blocked, bool)
        assert isinstance(result.results, dict)
        
        # Verify metric results
        results = result.results
        assert "faithfulness" in results
        assert "clarity" in results
        
        # Verify metric scores
        for metric_name, metric_result in results.items():
            assert isinstance(metric_result, dict) or hasattr(metric_result, "score")
            if isinstance(metric_result, dict) and "error" in metric_result:
                # Skip score assertion if error is present
                continue
            if hasattr(metric_result, "score"):
                assert isinstance(metric_result.score, float)
                assert 0 <= metric_result.score <= 100
            else:
                assert "score" in metric_result
                assert isinstance(metric_result["score"], float)
                assert 0 <= metric_result["score"] <= 100

    @patch("trustwise.sdk.metrics.v3.metrics.faithfulness.FaithfulnessMetric.evaluate")
    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_evaluate_with_custom_metrics(
        self,
        mock_post: Any,
        mock_faithfulness_evaluate: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list,
        sample_response: str
    ) -> None:
        """Test response evaluation with custom metrics."""
        mock_post.return_value = get_mock_response("guardrails/evaluate")
        mock_faithfulness_evaluate.return_value = get_mock_response("safety/faithfulness")
        guardrail = Guardrail(
            trustwise_client=sdk,
            thresholds={"faithfulness": 80, "clarity": 70}
        )
        result = guardrail.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        
        assert isinstance(result, GuardrailResponse)
        assert isinstance(result.passed, bool)
        assert isinstance(result.blocked, bool)
        assert isinstance(result.results, dict)
        
        # Verify metric results
        results = result.results
        assert "faithfulness" in results
        assert "clarity" in results

    @patch("trustwise.sdk.metrics.v3.metrics.faithfulness.FaithfulnessMetric.evaluate")
    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_evaluate_without_blocking(
        self,
        mock_post: Any,
        mock_faithfulness_evaluate: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list,
        sample_response: str
    ) -> None:
        """Test response evaluation without blocking."""
        mock_post.return_value = get_mock_response("guardrails/evaluate")
        mock_faithfulness_evaluate.return_value = get_mock_response("safety/faithfulness")
        guardrail = Guardrail(
            trustwise_client=sdk,
            thresholds={"faithfulness": 80, "clarity": 70},
            block_on_failure=False
        )
        result = guardrail.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        
        assert isinstance(result, GuardrailResponse)
        assert isinstance(result.passed, bool)
        assert isinstance(result.blocked, bool)
        assert result.blocked is False  # Should not block even if failed

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_invalid_thresholds(self, mock_post, sdk):
        """Test handling of invalid thresholds."""
        with pytest.raises(ValueError):
            Guardrail(
                trustwise_client=sdk,
                thresholds={
                    "faithfulness": 150  # Invalid threshold > 100
                }
            )
        
        with pytest.raises(ValueError):
            Guardrail(
                trustwise_client=sdk,
                thresholds={
                    "prompt_injection": 150  # Invalid threshold > 100
                }
            )

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_missing_parameters(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list
    ) -> None:
        """Test handling of missing parameters."""
        mock_post.side_effect = ValueError("Missing parameters")
        guardrail = Guardrail(
            trustwise_client=sdk,
            thresholds={"faithfulness": 80}
        )
        with pytest.raises(ValueError):
            guardrail.evaluate(
                query=sample_query,
                context=sample_context,
                response=None
            )

    @patch("trustwise.sdk.metrics.v3.metrics.prompt_injection.PromptInjectionMetric.evaluate")
    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_evaluate_with_prompt_injection(
        self,
        mock_post: Any,
        mock_prompt_injection_evaluate: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list,
        sample_response: str
    ) -> None:
        """Test response evaluation with prompt injection detection."""
        mock_post.return_value = get_mock_response("guardrails/evaluate")
        mock_prompt_injection_evaluate.return_value = get_mock_response("safety/faithfulness")
        guardrail = Guardrail(
            trustwise_client=sdk,
            thresholds={"prompt_injection": 0.1}  # Low threshold to detect injection attempts
        )
        result = guardrail.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        
        assert isinstance(result, GuardrailResponse)
        assert isinstance(result.passed, bool)
        assert isinstance(result.blocked, bool)
        assert isinstance(result.results, dict)
        
        # Verify prompt injection metric
        results = result.results
        assert "prompt_injection" in results
        assert isinstance(results["prompt_injection"], dict)
        assert "result" in results["prompt_injection"]
        assert "passed" in results["prompt_injection"]
        assert "result" in results["prompt_injection"]
        assert isinstance(results["prompt_injection"]["result"], dict)
        assert "score" in results["prompt_injection"]["result"]
        assert isinstance(results["prompt_injection"]["result"]["score"], float)
        assert 0 <= results["prompt_injection"]["result"]["score"] <= 100 