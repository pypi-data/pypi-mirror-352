import pytest

import trustwise

# List of all symbols to check for importability from trustwise
IMPORTABLES = [
    # Exceptions
    "TrustwiseSDKError",
    "TrustwiseValidationError",
    "TrustwiseAPIError",
    # Types
    "Facts",
    "Fact",
    "Context",
    "ContextNode",
    "FaithfulnessRequest", "FaithfulnessResponse",
    "AnswerRelevancyRequest", "AnswerRelevancyResponse",
    "ContextRelevancyRequest", "ContextRelevancyResponse",
    "SummarizationRequest", "SummarizationResponse",
    "PIIEntity", "PIIRequest", "PIIResponse",
    "PromptInjectionRequest", "PromptInjectionResponse",
    "ClarityRequest", "ClarityResponse",
    "HelpfulnessRequest", "HelpfulnessResponse",
    "FormalityRequest", "FormalityResponse",
    "SimplicityRequest", "SimplicityResponse",
    "SensitivityRequest", "SensitivityResponse",
    "ToxicityRequest", "ToxicityResponse",
    "ToneRequest", "ToneResponse",
    "CostRequest", "CostResponse",
    "CarbonRequest", "CarbonResponse",
    "GuardrailResponse",
]

@pytest.mark.parametrize("symbol", trustwise.__all__)
def test_importable(symbol):
    obj = getattr(trustwise, symbol, None)
    assert obj is not None, f"{symbol} should be importable from trustwise"

def test_non_exported_symbol_not_importable():
    assert not hasattr(trustwise, "make_status_error_from_response"), (
        "make_status_error_from_response should NOT be importable from trustwise"
    ) 