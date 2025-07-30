"""Unit tests for Trustwise configuration."""

import os
from unittest.mock import patch
from urllib.parse import urlparse

import pytest

from trustwise.sdk.config import TrustwiseConfig


class TestTrustwiseConfig:
    """Test cases for Trustwise configuration."""
    
    def test_default_base_url(self):
        """Test default base URL when no value is provided."""
        config = TrustwiseConfig(api_key="test-key")
        assert config.base_url == "https://api.trustwise.ai/"
    
    def test_custom_base_url(self):
        """Test custom base URL."""
        # Test with trailing slash
        custom_url = "https://custom.trustwise.ai/"
        config = TrustwiseConfig(api_key="test-key", base_url=custom_url)
        assert config.base_url == custom_url
        
        # Test without trailing slash
        custom_url = "https://custom.trustwise.ai"
        config = TrustwiseConfig(api_key="test-key", base_url=custom_url)
        assert config.base_url == f"{custom_url}/"
    
    def test_base_url_from_env(self):
        """Test base URL from environment variable."""
        # Test with trailing slash
        custom_url = "https://env.trustwise.ai/"
        with patch.dict(os.environ, {"TW_BASE_URL": custom_url}):
            config = TrustwiseConfig(api_key="test-key")
            assert config.base_url == custom_url
        
        # Test without trailing slash
        custom_url = "https://env.trustwise.ai"
        with patch.dict(os.environ, {"TW_BASE_URL": custom_url}):
            config = TrustwiseConfig(api_key="test-key")
            assert config.base_url == f"{custom_url}/"
    
    def test_api_key_required_validation(self):
        """Test API key validation."""
        # Test missing API key
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                TrustwiseConfig()
            assert "API key must be provided" in str(exc_info.value)
        
        # Test empty API key
        with pytest.raises(ValueError) as exc_info:
            TrustwiseConfig(api_key="")
        assert "API key must be provided" in str(exc_info.value)
        
        # Test None API key
        with pytest.raises(ValueError) as exc_info:
            TrustwiseConfig(api_key=None)
        assert "API key must be provided either directly or through TW_API_KEY environment variable" in str(exc_info.value)
        
        # Test invalid API key type
        with pytest.raises(ValueError) as exc_info:
            TrustwiseConfig(api_key=123)  # type: ignore
        assert "API key must be a valid string" in str(exc_info.value)
    
    def test_api_key_from_env(self):
        """Test API key from environment variable."""
        with patch.dict(os.environ, {"TW_API_KEY": "env-key"}):
            config = TrustwiseConfig()
            assert config.api_key == "env-key"
    
    def test_api_key_precedence(self):
        """Test that direct API key takes precedence over environment variable."""
        with patch.dict(os.environ, {"TW_API_KEY": "env-key"}):
            config = TrustwiseConfig(api_key="direct-key")
            assert config.api_key == "direct-key"
    
    def test_base_url_validation(self):
        """Test base URL validation."""
        # Test invalid base URL format
        with pytest.raises(ValueError) as exc_info:
            TrustwiseConfig(api_key="test-key", base_url="invalid-url")
        assert "Invalid base URL format" in str(exc_info.value)
        
        # Test invalid base URL type
        with pytest.raises(ValueError) as exc_info:
            TrustwiseConfig(api_key="test-key", base_url=123)  # type: ignore
        assert "Base URL must be a valid string" in str(exc_info.value)
        
        # Test missing scheme
        with pytest.raises(ValueError) as exc_info:
            TrustwiseConfig(api_key="test-key", base_url="trustwise.ai")
        assert "Invalid base URL format" in str(exc_info.value)
        
        # Test missing netloc
        with pytest.raises(ValueError) as exc_info:
            TrustwiseConfig(api_key="test-key", base_url="https://")
        assert "Invalid base URL format" in str(exc_info.value)
    
    def test_get_safety_url(self):
        """Test safety URL construction."""
        # Test with default base URL
        config = TrustwiseConfig(api_key="test-key")
        url = config.get_safety_url("v3")
        assert url == "https://api.trustwise.ai/safety/v3"
        assert urlparse(url).scheme == "https"
        
        # Test with custom base URL
        custom_url = "https://custom.trustwise.ai/api"
        config = TrustwiseConfig(api_key="test-key", base_url=custom_url)
        url = config.get_safety_url("v3")
        assert url == "https://custom.trustwise.ai/api/safety/v3"
    
    def test_get_alignment_url(self):
        """Test alignment URL construction."""
        # Test with default base URL
        config = TrustwiseConfig(api_key="test-key")
        url = config.get_alignment_url("v1")
        assert url == "https://api.trustwise.ai/alignment/v1"
        assert urlparse(url).scheme == "https"
        
        # Test with custom base URL
        custom_url = "https://custom.trustwise.ai/api"
        config = TrustwiseConfig(api_key="test-key", base_url=custom_url)
        url = config.get_alignment_url("v1")
        assert url == "https://custom.trustwise.ai/api/alignment/v1"
    
    def test_custom_base_url_with_paths(self):
        """Test URL construction with custom base URL."""
        # Test with trailing slash
        custom_url = "https://custom.trustwise.ai/api/"
        config = TrustwiseConfig(api_key="test-key", base_url=custom_url)
        assert config.get_safety_url("v3") == "https://custom.trustwise.ai/api/safety/v3"
        assert config.get_alignment_url("v1") == "https://custom.trustwise.ai/api/alignment/v1"
        
        # Test without trailing slash
        custom_url = "https://custom.trustwise.ai/api"
        config = TrustwiseConfig(api_key="test-key", base_url=custom_url)
        assert config.get_safety_url("v3") == "https://custom.trustwise.ai/api/safety/v3"
        assert config.get_alignment_url("v1") == "https://custom.trustwise.ai/api/alignment/v1"

def test_post_raises_trustwise_api_error_on_non_200(monkeypatch):
    import requests

    from trustwise.sdk.client import TrustwiseClient
    from trustwise.sdk.config import TrustwiseConfig
    from trustwise.sdk.exceptions import TrustwiseAPIError

    class MockResponse:
        def __init__(self, status_code, json_data=None, text_data=None):
            self.status_code = status_code
            self._json_data = json_data
            self.text = text_data or ""
            self.headers = {}
            self.raw = type("raw", (), {"closed": False})()
        def json(self):
            if self._json_data is not None:
                return self._json_data
            raise ValueError("No JSON")

    def mock_post(*args, **kwargs):
        return MockResponse(401, json_data={"message": "Auth error"}, text_data='{"message": "Auth error"}')

    monkeypatch.setattr(requests, "post", mock_post)
    config = TrustwiseConfig(api_key="bad", base_url="https://api.example.com/")
    client = TrustwiseClient(config)
    with pytest.raises(TrustwiseAPIError) as exc_info:
        client._post("https://api.example.com/test", data={})
    assert exc_info.value.status_code == 401
    assert exc_info.value.response == {"message": "Auth error"}
    assert "Auth error" in str(exc_info.value)


def test_post_raises_trustwise_api_error_on_non_json(monkeypatch):
    import requests

    from trustwise.sdk.client import TrustwiseClient
    from trustwise.sdk.config import TrustwiseConfig
    from trustwise.sdk.exceptions import TrustwiseAPIError

    class MockResponse:
        def __init__(self, status_code, text_data=None):
            self.status_code = status_code
            self.text = text_data or ""
            self.headers = {}
            self.raw = type("raw", (), {"closed": False})()
        def json(self):
            raise ValueError("No JSON")

    def mock_post(*args, **kwargs):
        return MockResponse(500, text_data="Internal Server Error")

    monkeypatch.setattr(requests, "post", mock_post)
    config = TrustwiseConfig(api_key="bad", base_url="https://api.example.com/")
    client = TrustwiseClient(config)
    with pytest.raises(TrustwiseAPIError) as exc_info:
        client._post("https://api.example.com/test", data={})
    assert exc_info.value.status_code == 500
    assert exc_info.value.response == "Internal Server Error"
    assert "Internal Server Error" in str(exc_info.value) 