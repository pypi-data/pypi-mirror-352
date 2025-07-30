import os

import pytest

from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.config import TrustwiseConfig


@pytest.fixture
def api_key():
    """Get API key from environment variable or use a mock key for testing."""
    key = os.getenv("TW_API_KEY", "mock-api-key-for-testing")
    return key

@pytest.fixture
def sdk(api_key):
    """Create a Trustwise SDK instance."""
    config = TrustwiseConfig(api_key=api_key, base_url="https://random.trustwise.ai")
    return TrustwiseSDK(config)

@pytest.fixture
def sample_context():
    """Sample context data for testing."""
    return [
        {
            "node_text": "According to Crawford's Complete Auto Maintenance Guide, to check tire pressure, you'll need a tire pressure gauge. These can be purchased at auto parts stores and service stations for as little as $1-7.",
            "node_score": 0.95,
            "node_id": "doc:idx:1"
        },
        {
            "node_text": "Steps to check tire pressure: 1. Remove the valve cap from each tire 2. Align the gauge up to the valve 3. Press the gauge onto the valve with firm direct pressure and then release 4. For pen gauges, you'll see the measuring stick pushed out displaying the pressure reading 5. Fill the tire with air if needed, then recheck until you reach the desired pressure",
            "node_score": 0.92,
            "node_id": "doc:idx:2"
        },
        {
            "node_text": "The recommended tire pressure for your vehicle can be found on a sticker in the driver's door jamb, in the vehicle owner's manual, or sometimes on the inside of the fuel filler door. Most passenger vehicles have a recommended pressure between 32-35 PSI.",
            "node_score": 0.85,
            "node_id": "doc:idx:3"
        }
    ]

@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "How do I check my tire pressure?"

@pytest.fixture
def sample_response():
    """Sample response for testing."""
    return "According to Crawford's Guide, you need a tire pressure gauge which you can buy at an auto parts store or service station for about $1-7. To check pressure: remove the valve cap, press the gauge onto the valve firmly, and read the measurement. If needed, add air and recheck until you reach the right pressure." 