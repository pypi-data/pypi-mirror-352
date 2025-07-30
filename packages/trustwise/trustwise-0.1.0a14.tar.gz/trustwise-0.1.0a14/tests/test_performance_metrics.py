from typing import Any
from unittest.mock import patch

import pytest

from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.exceptions import TrustwiseAPIError, TrustwiseValidationError
from trustwise.sdk.types import (
    CarbonRequest,
    CarbonResponse,
    CostResponse,
)

from .helpers import get_mock_response


class TestPerformanceMetricsV1:
    """Test suite for Performance Metrics API v1."""

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_openai_llm(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation for OpenAI LLM."""
        mock_post.return_value = get_mock_response("performance/v1/cost")
        result = sdk.metrics.cost.evaluate(
            model_name="gpt-3.5-turbo",
            model_type="LLM",
            model_provider="OpenAI",
            number_of_queries=5,
            total_prompt_tokens=950,
            total_completion_tokens=50
        )
        assert isinstance(result, CostResponse)
        assert isinstance(result.cost_estimate_per_run, float)
        assert isinstance(result.total_project_cost_estimate, float)
        # Test JSON output
        json_str = result.to_json()
        import json as _json
        data = _json.loads(json_str)
        assert data["cost_estimate_per_run"] == result.cost_estimate_per_run
        assert data["total_project_cost_estimate"] == result.total_project_cost_estimate

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_huggingface_llm(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation for Hugging Face LLM."""
        mock_post.return_value = get_mock_response("performance/v1/cost")
        result = sdk.metrics.cost.evaluate(
            model_name="mistral-7b",
            model_type="LLM",
            model_provider="HuggingFace",
            number_of_queries=5,
            total_prompt_tokens=950,
            total_completion_tokens=50,
            instance_type="a1.large",
            average_latency=653
        )
        assert isinstance(result, CostResponse)
        assert isinstance(result.cost_estimate_per_run, float)
        assert isinstance(result.total_project_cost_estimate, float)
        # Test JSON output
        json_str = result.to_json()
        import json as _json
        data = _json.loads(json_str)
        assert data["cost_estimate_per_run"] == result.cost_estimate_per_run
        assert data["total_project_cost_estimate"] == result.total_project_cost_estimate

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_azure_reranker(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation for Azure Reranker."""
        mock_post.return_value = get_mock_response("performance/v1/cost")
        result = sdk.metrics.cost.evaluate(
            model_name="azure-reranker",
            model_type="Reranker",
            model_provider="Azure Reranker",
            number_of_queries=5,
            total_prompt_tokens=100,
            total_completion_tokens=10
        )
        assert isinstance(result, CostResponse)
        assert isinstance(result.cost_estimate_per_run, float)
        assert isinstance(result.total_project_cost_estimate, float)
        # Test JSON output
        json_str = result.to_json()
        import json as _json
        data = _json.loads(json_str)
        assert data["cost_estimate_per_run"] == result.cost_estimate_per_run
        assert data["total_project_cost_estimate"] == result.total_project_cost_estimate

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_together_reranker(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation for Together Reranker."""
        mock_post.return_value = get_mock_response("performance/v1/cost")
        result = sdk.metrics.cost.evaluate(
            model_name="together-reranker",
            model_type="Reranker",
            model_provider="Together Reranker",
            number_of_queries=5,
            total_prompt_tokens=100,
            total_completion_tokens=10,
            total_tokens=1000
        )
        assert isinstance(result, CostResponse)
        assert isinstance(result.cost_estimate_per_run, float)
        assert isinstance(result.total_project_cost_estimate, float)
        # Test JSON output
        json_str = result.to_json()
        import json as _json
        data = _json.loads(json_str)
        assert data["cost_estimate_per_run"] == result.cost_estimate_per_run
        assert data["total_project_cost_estimate"] == result.total_project_cost_estimate

    def test_cost_invalid_model_type(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation with invalid model type."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.cost.evaluate(
                model_name="gpt-3.5-turbo",
                model_type="Invalid",
                model_provider="OpenAI",
                number_of_queries=5,
                total_prompt_tokens=950,
                total_completion_tokens=50
            )
        assert "Error in 'CostRequest'" in str(excinfo.value)
        assert "model_type" in str(excinfo.value)

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_missing_required_fields_llm(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation with missing required fields for LLM."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.cost.evaluate(
                model_name="gpt-3.5-turbo",
                model_type="LLM",
                model_provider="OpenAI",
                number_of_queries=5
            )
        msg = str(excinfo.value)
        assert "'total_prompt_tokens'" in msg
        assert "'total_completion_tokens'" in msg

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_missing_required_fields_huggingface(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation with missing required fields for Hugging Face."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.cost.evaluate(
                model_name="mistral-7b",
                model_type="LLM",
                model_provider="HuggingFace",
                number_of_queries=5,
                total_prompt_tokens=950
            )
        msg = str(excinfo.value)
        assert "'total_completion_tokens'" in msg

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_invalid_fields_openai(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test cost evaluation with invalid fields for OpenAI."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.cost.evaluate(
                model_name="gpt-3.5-turbo",
                model_type="LLM",
                model_provider="OpenAI",
                number_of_queries=-1,
                total_prompt_tokens=950,
                total_completion_tokens=50
            )
        assert "Error in 'CostRequest'" in str(excinfo.value)
        assert "number_of_queries" in str(excinfo.value)

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_carbon(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test carbon evaluation."""
        mock_post.return_value = get_mock_response("performance/v1/carbon")
        request = CarbonRequest(
            processor_name="RTX 3080",
            provider_name="aws",
            provider_region="us-east-1",
            instance_type="a1.metal",
            average_latency=653
        )
        result = sdk.metrics.carbon.evaluate(**request.model_dump())
        assert isinstance(result, CarbonResponse)
        assert isinstance(result.carbon_emitted, float)
        assert isinstance(result.sci_per_api_call, float)
        assert isinstance(result.sci_per_10k_calls, float)
        # Test JSON output
        json_str = result.to_json()
        import json as _json
        data = _json.loads(json_str)
        assert data["carbon_emitted"] == result.carbon_emitted
        assert data["sci_per_api_call"] == result.sci_per_api_call
        assert data["sci_per_10k_calls"] == result.sci_per_10k_calls

    def test_batch_evaluate_not_implemented(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test that batch evaluation is not implemented."""
        with pytest.raises(NotImplementedError):
            sdk.metrics.cost.batch_evaluate([])

    def test_explain_not_implemented(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test that explanation is not implemented."""
        with pytest.raises(NotImplementedError):
            sdk.metrics.cost.explain()

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_api_error_detail(self, mock_post: Any, sdk: TrustwiseSDK) -> None:
        """Test that API errors with 'detail' are raised as is."""
        mock_post.side_effect = TrustwiseAPIError(
            "Error code: 422 - {'detail': ['Invalid input: missing required fields.']}",
            {"detail": ["Invalid input: missing required fields."]},
            422
        )
        with pytest.raises(TrustwiseAPIError) as excinfo:
            sdk.metrics.cost.evaluate(
                model_name="gpt-3.5-turbo",
                model_type="LLM",
                model_provider="OpenAI",
                number_of_queries=5,
                total_prompt_tokens=950,
                total_completion_tokens=50
            )
        assert "Invalid input" in str(excinfo.value)
        assert excinfo.value.status_code == 422

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_cost_pydantic_validation_error(self, mock_post: Any, sdk: TrustwiseSDK) -> None:
        """Test that Pydantic validation errors are user-friendly if backend returns 200 but missing fields."""
        # Simulate a 200 response with missing required fields
        mock_post.return_value = {}
        with pytest.raises(Exception) as excinfo:
            sdk.metrics.cost.evaluate(
                model_name="gpt-3.5-turbo",
                model_type="LLM",
                model_provider="OpenAI",
                number_of_queries=5,
                total_prompt_tokens=950,
                total_completion_tokens=50
            )
        msg = str(excinfo.value)
        assert (
            "Failed to parse cost response" in msg
            or "validation error" in msg
            or "CostResponse" in msg
        )
        assert "cost_estimate_per_run" in msg
        assert "total_project_cost_estimate" in msg 