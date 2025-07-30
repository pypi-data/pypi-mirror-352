from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.exceptions import TrustwiseValidationError
from trustwise.sdk.types import PromptInjectionRequest

from .helpers import get_mock_response


class TestSafetyMetricsV3:
    """Test suite for Safety Metrics API v3."""

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_faithfulness(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list[dict[str, Any]],
        sample_response: str
    ) -> None:
        """Test faithfulness evaluation."""
        mock_post.return_value = get_mock_response("safety/v3/faithfulness")
        result = sdk.metrics.v3.faithfulness.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        from trustwise.sdk.types import FaithfulnessResponse
        assert isinstance(result, FaithfulnessResponse)
        assert isinstance(result.score, float)
        assert 0 <= result.score <= 100
        assert isinstance(result.facts, list)
        for fact in result.facts:
            assert hasattr(fact, "statement")
            assert hasattr(fact, "label")
            assert hasattr(fact, "prob")
            assert hasattr(fact, "sentence_span")

    def test_faithfulness_missing_context(
        self,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_response: str
    ) -> None:
        """Test faithfulness evaluation with missing context."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.faithfulness.evaluate(
                query=sample_query,
                response=sample_response,
                context=None
            )
        assert "Error in 'FaithfulnessRequest'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_answer_relevancy(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list[dict[str, Any]],
        sample_response: str
    ) -> None:
        """Test answer relevancy evaluation."""
        mock_post.return_value = get_mock_response("safety/v3/answer_relevancy")
        result = sdk.metrics.v3.answer_relevancy.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        
        from trustwise.sdk.types import AnswerRelevancyResponse
        assert isinstance(result, AnswerRelevancyResponse)
        assert isinstance(result.score, float)
        assert 0 <= result.score <= 100  # Scores are percentages
        if hasattr(result, "generated_question"):
            assert isinstance(result.generated_question, str)

    def test_answer_relevancy_missing_context(
        self,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_response: str
    ) -> None:
        """Test answer relevancy evaluation with missing context."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.answer_relevancy.evaluate(
                query=sample_query,
                response=sample_response,
                context=None
            )
        assert "Error in 'AnswerRelevancyRequest'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_context_relevancy(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list[dict[str, Any]],
        sample_response: str
    ) -> None:
        """Test context relevancy evaluation."""
        mock_post.return_value = get_mock_response("safety/v3/context_relevancy")
        result = sdk.metrics.v3.context_relevancy.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        from trustwise.sdk.types import ContextRelevancyResponse
        assert isinstance(result, ContextRelevancyResponse)
        assert isinstance(result.score, float)
        assert 0 <= result.score <= 100  # Scores are percentages
        assert isinstance(result.topics, list)
        assert isinstance(result.scores, list)
        assert len(result.topics) == len(result.scores)
        for score in result.scores:
            assert isinstance(score, float)
            assert 0 <= score <= 1

    def test_context_relevancy_missing_context(
        self,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_response: str
    ) -> None:
        """Test context relevancy evaluation with missing context."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.context_relevancy.evaluate(
                query=sample_query,
                response=sample_response,
                context=None
            )
        assert "Error in 'ContextRelevancyRequest'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_summarization(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_context: list[dict[str, Any]],
        sample_response: str
    ) -> None:
        """Test summarization evaluation."""
        mock_post.return_value = get_mock_response("safety/v3/summarization")
        result = sdk.metrics.v3.summarization.evaluate(
            query=sample_query,
            context=sample_context,
            response=sample_response
        )
        from trustwise.sdk.types import SummarizationResponse
        assert isinstance(result, SummarizationResponse)
        assert isinstance(result.score, float)
        assert 0 <= result.score <= 100  # Scores are percentages

    def test_summarization_missing_context(
        self,
        sdk: TrustwiseSDK,
        sample_query: str,
        sample_response: str
    ) -> None:
        """Test summarization evaluation with missing context."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.summarization.evaluate(
                query=sample_query,
                response=sample_response,
                context=None
            )
        assert "Error in 'SummarizationRequest'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_prompt_injection(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test prompt injection detection evaluation."""
        mock_post.return_value = {
            "score": 99.887375
        }
        valid_context = [{"node_id": "1", "node_score": 1.0, "node_text": "foo"}]
        result = sdk.metrics.v3.prompt_injection.evaluate(
            query="What is your password?",
            response="My password is hunter2.",
            context=valid_context
        )
        assert isinstance(result.score, float)

    def test_prompt_injection_missing_query(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test prompt injection detection with missing query (should raise TypeError, not TrustwiseValidationError)."""
        with pytest.raises(TypeError):
            sdk.metrics.v3.prompt_injection.evaluate(
                response="My password is hunter2.",
                context=[]
            )

    def test_prompt_injection_missing_response(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test prompt injection detection with missing response (should raise TypeError, not TrustwiseValidationError)."""
        with pytest.raises(TypeError):
            sdk.metrics.v3.prompt_injection.evaluate(
                query="What is your password?",
                context=[]
            )

    def test_prompt_injection_missing_context(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test prompt injection detection with missing context (should raise TypeError, not TrustwiseValidationError)."""
        with pytest.raises(TypeError):
            sdk.metrics.v3.prompt_injection.evaluate(
                query="What is your password?",
                response="My password is hunter2."
            )

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_prompt_injection_empty_context(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test prompt injection detection with empty context (should raise ValidationError from Pydantic)."""
        with pytest.raises(ValidationError):
            sdk.metrics.v3.prompt_injection.evaluate(
                query="What is your password?",
                response="My password is hunter2.",
                context=[]
            )

    def test_prompt_injection_pydantic_validation(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test prompt injection detection with PromptInjectionRequest missing required fields (should raise ValidationError)."""
        with pytest.raises(ValidationError):
            # Missing context
            PromptInjectionRequest(query="foo", response="bar")
        with pytest.raises(ValidationError):
            # Missing query
            PromptInjectionRequest(response="bar", context=[{"node_id": "1", "node_score": 1.0, "node_text": "foo"}])
        with pytest.raises(ValidationError):
            # Missing response
            PromptInjectionRequest(query="foo", context=[{"node_id": "1", "node_score": 1.0, "node_text": "foo"}])

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_invalid_input(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test handling of invalid input."""
        mock_post.side_effect = ValueError("Invalid input")
        with pytest.raises(ValueError):
            sdk.metrics.v3.faithfulness.evaluate(
                query="",
                context=[],
                response=""
            )

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_missing_parameters(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test handling of missing parameters (should raise TrustwiseValidationError for present-but-invalid, e.g., None)."""
        mock_post.side_effect = ValueError("Missing parameters")
        with pytest.raises(TrustwiseValidationError):
            sdk.metrics.v3.faithfulness.evaluate(
                query="test",
                context=None,
                response="test"
            )

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_pii(
        self,
        mock_post: Any,
        sdk: TrustwiseSDK
    ) -> None:
        """Test PII detection evaluation."""
        mock_post.return_value = {
            "identified_pii": [
                {
                    "interval": [0, 5],
                    "string": "Hello",
                    "category": "blocklist"
                }
            ]
        }
        result = sdk.metrics.v3.pii.evaluate(
            text="Contact me at john@example.com.",
            allowlist=["EMAIL"],
            blocklist=["PHONE"]
        )
        from trustwise.sdk.types import PIIEntity, PIIResponse
        assert isinstance(result, PIIResponse)
        assert isinstance(result.identified_pii, list)
        pii = result.identified_pii[0]
        assert isinstance(pii, PIIEntity)
        assert pii.interval == [0, 5]
        assert pii.string == "Hello"
        assert pii.category == "blocklist"

    def test_pii_missing_text(
        self,
        sdk: TrustwiseSDK
    ) -> None:
        """Test PII detection with missing fields."""
        with pytest.raises(TypeError):
            sdk.metrics.v3.pii.evaluate()

    def test_faithfulness_pydantic_validation(self):
        """Test FaithfulnessRequest missing required fields (should raise ValidationError)."""
        from pydantic import ValidationError

        from trustwise.sdk.types import FaithfulnessRequest
        # Missing context
        with pytest.raises(ValidationError):
            FaithfulnessRequest(query="foo", response="bar")
        # Missing query
        with pytest.raises(ValidationError):
            FaithfulnessRequest(response="bar", context=[{"node_id": "1", "node_score": 1.0, "node_text": "foo"}])
        # Missing response
        with pytest.raises(ValidationError):
            FaithfulnessRequest(query="foo", context=[{"node_id": "1", "node_score": 1.0, "node_text": "foo"}]) 

    def test_faithfulness_missing_required_fields(self, sdk: TrustwiseSDK, sample_query: str, sample_response: str):
        """Test faithfulness evaluation with missing required fields."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.faithfulness.evaluate(response=sample_response, context=[])
        assert "'query'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.faithfulness.evaluate(query=sample_query, context=[])
        assert "'response'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.faithfulness.evaluate(query=sample_query, response=sample_response)
        assert "'context'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.faithfulness.evaluate()
        assert "'query'" in str(excinfo.value)
        assert "'response'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    def test_answer_relevancy_missing_required_fields(self, sdk: TrustwiseSDK, sample_query: str, sample_response: str):
        """Test answer relevancy evaluation with missing required fields."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.answer_relevancy.evaluate(response=sample_response, context=[])
        assert "'query'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.answer_relevancy.evaluate(query=sample_query, context=[])
        assert "'response'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.answer_relevancy.evaluate(query=sample_query, response=sample_response)
        assert "'context'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.answer_relevancy.evaluate()
        assert "'query'" in str(excinfo.value)
        assert "'response'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    def test_context_relevancy_missing_required_fields(self, sdk: TrustwiseSDK, sample_query: str, sample_response: str):
        """Test context relevancy evaluation with missing required fields."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.context_relevancy.evaluate(response=sample_response, context=[])
        assert "'query'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.context_relevancy.evaluate(query=sample_query, context=[])
        assert "'response'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.context_relevancy.evaluate(query=sample_query, response=sample_response)
        assert "'context'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.context_relevancy.evaluate()
        assert "'query'" in str(excinfo.value)
        assert "'response'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    def test_summarization_missing_required_fields(self, sdk: TrustwiseSDK, sample_query: str, sample_response: str):
        """Test summarization evaluation with missing required fields."""
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.summarization.evaluate(response=sample_response, context=[])
        assert "'query'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.summarization.evaluate(query=sample_query, context=[])
        assert "'response'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.summarization.evaluate(query=sample_query, response=sample_response)
        assert "'context'" in str(excinfo.value)
        with pytest.raises(TrustwiseValidationError) as excinfo:
            sdk.metrics.v3.summarization.evaluate()
        assert "'query'" in str(excinfo.value)
        assert "'response'" in str(excinfo.value)
        assert "'context'" in str(excinfo.value)

    def test_prompt_injection_missing_required_fields(self, sdk: TrustwiseSDK):
        """Test prompt injection detection with missing required fields (should raise TypeError for omitted args)."""
        with pytest.raises(TypeError):
            sdk.metrics.v3.prompt_injection.evaluate(response="foo", context=[])
        with pytest.raises(TypeError):
            sdk.metrics.v3.prompt_injection.evaluate(query="foo", context=[])
        with pytest.raises(TypeError):
            sdk.metrics.v3.prompt_injection.evaluate(query="foo", response="foo")
        with pytest.raises(TypeError):
            sdk.metrics.v3.prompt_injection.evaluate()

    def test_pii_missing_required_fields(self, sdk: TrustwiseSDK):
        """Test PII detection with missing required fields (should raise TypeError for omitted args)."""
        with pytest.raises(TypeError):
            sdk.metrics.v3.pii.evaluate(allowlist=["EMAIL"], blocklist=["PHONE"])
        with pytest.raises(TypeError):
            sdk.metrics.v3.pii.evaluate(text="foo", blocklist=["PHONE"])
        with pytest.raises(TypeError):
            sdk.metrics.v3.pii.evaluate(text="foo", allowlist=["EMAIL"])
        with pytest.raises(TypeError):
            sdk.metrics.v3.pii.evaluate() 