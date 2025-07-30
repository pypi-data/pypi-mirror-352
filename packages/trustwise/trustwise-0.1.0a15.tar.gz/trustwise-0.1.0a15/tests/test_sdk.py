from typing import Any
from unittest.mock import patch

import pytest

from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.config import TrustwiseConfig
from trustwise.sdk.types import FaithfulnessResponse

from .helpers import get_mock_response


class TestTrustwiseSDK:
    """Test suite for the main Trustwise SDK class."""

    def test_sdk_initialization(self, api_key: str) -> None:
        """Test SDK initialization."""
        config = TrustwiseConfig(api_key=api_key)
        sdk = TrustwiseSDK(config)
        assert isinstance(sdk, TrustwiseSDK)
        assert hasattr(sdk, "client")

    def test_get_versions(self, sdk: TrustwiseSDK) -> None:
        """Test version information retrieval."""
        versions = sdk.get_versions()
        
        assert isinstance(versions, dict)
        assert "safety" in versions
        assert "alignment" in versions
        assert "performance" in versions
        assert isinstance(versions["safety"], list)
        assert isinstance(versions["alignment"], list)
        assert isinstance(versions["performance"], list)
        assert "v3" in versions["safety"]
        assert "v1" in versions["alignment"]
        assert "v1" in versions["performance"]

    # def test_safety_namespace(self, sdk: TrustwiseSDK) -> None:
    #     """Test safety namespace access."""
    #     # Test direct version access
    #     assert hasattr(sdk.safety, "v3")

    def test_guardrails_namespace(self, sdk: TrustwiseSDK) -> None:
        """Test guardrails namespace access."""
        assert hasattr(sdk, "guardrails")
        assert callable(sdk.guardrails)

    # def test_alignment_namespace(self, sdk: TrustwiseSDK) -> None:
    #     """Test alignment namespace access."""
    #     # Test direct version access
    #     assert hasattr(sdk.alignment, "v1")

    def test_invalid_api_key(self) -> None:
        """Test SDK initialization with invalid API key."""
        with pytest.raises(ValueError):
            config = TrustwiseConfig(api_key="")
            TrustwiseSDK(config)

        with pytest.raises(ValueError):
            config = TrustwiseConfig(api_key=None)
            TrustwiseSDK(config)

    def test_invalid_base_url(self, api_key: str) -> None:
        """Test SDK initialization with invalid base URL."""
        with pytest.raises(ValueError):
            config = TrustwiseConfig(api_key=api_key, base_url="")
            TrustwiseSDK(config)

        with pytest.raises(ValueError):
            config = TrustwiseConfig(api_key=api_key, base_url="not-a-url")
            TrustwiseSDK(config)

    def test_namespace_version_consistency(self, sdk: TrustwiseSDK) -> None:
        """Test that namespace versions are consistent with get_versions()."""
        # Only metrics namespace is supported now

    @patch("trustwise.sdk.client.TrustwiseClient._post")
    def test_sdk_actual_usage(self, mock_post: Any, api_key: str) -> None:
        """Test actual SDK usage to catch import and initialization issues."""
        # Set up mock responses
        mock_post.return_value = get_mock_response("safety/v3/faithfulness")
        
        config = TrustwiseConfig(api_key=api_key)
        sdk = TrustwiseSDK(config)
        
        # Test guardrails initialization
        guardrail = sdk.guardrails(
            thresholds={
                "faithfulness": 80,
                "clarity": 70
            }
        )
        assert guardrail is not None
        
        # Test basic metric evaluation
        result = sdk.metrics.faithfulness.evaluate(
            query="What is the capital of France?",
            response="The capital of France is Paris.",
            context=[{
                "node_text": "Paris is the capital of France.",
                "node_score": 0.95,
                "node_id": "doc:idx:1"
            }]
        )
        assert isinstance(result, FaithfulnessResponse)
        assert hasattr(result, "score")
        assert isinstance(result.score, float) 