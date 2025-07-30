from typing import Any

from trustwise.sdk.metrics.v3 import (
    AnswerRelevancyMetric,
    CarbonMetric,
    ClarityMetric,
    ContextRelevancyMetric,
    CostMetric,
    FaithfulnessMetric,
    FormalityMetric,
    HelpfulnessMetric,
    PIIMetric,
    PromptInjectionMetric,
    SensitivityMetric,
    SimplicityMetric,
    SummarizationMetric,
    ToneMetric,
    ToxicityMetric,
)


class MetricsV3:
    def __init__(self, client: Any) -> None:
        self.faithfulness = FaithfulnessMetric(client)
        self.answer_relevancy = AnswerRelevancyMetric(client)
        self.context_relevancy = ContextRelevancyMetric(client)
        self.summarization = SummarizationMetric(client)
        self.pii = PIIMetric(client)
        self.prompt_injection = PromptInjectionMetric(client)
        self.clarity = ClarityMetric(client)
        self.formality = FormalityMetric(client)
        self.helpfulness = HelpfulnessMetric(client)
        self.simplicity = SimplicityMetric(client)
        self.tone = ToneMetric(client)
        self.toxicity = ToxicityMetric(client)
        self.sensitivity = SensitivityMetric(client)
        self.cost = CostMetric(client)
        self.carbon = CarbonMetric(client)

class Metrics:
    def __init__(self, client: Any) -> None:
        self.v3 = MetricsV3(client)
        # Expose v3 metrics directly
        self.faithfulness = self.v3.faithfulness
        self.answer_relevancy = self.v3.answer_relevancy
        self.context_relevancy = self.v3.context_relevancy
        self.summarization = self.v3.summarization
        self.pii = self.v3.pii
        self.prompt_injection = self.v3.prompt_injection
        self.clarity = self.v3.clarity
        self.formality = self.v3.formality
        self.helpfulness = self.v3.helpfulness
        self.simplicity = self.v3.simplicity
        self.tone = self.v3.tone
        self.toxicity = self.v3.toxicity
        self.sensitivity = self.v3.sensitivity
        self.cost = self.v3.cost
        self.carbon = self.v3.carbon

    @property
    def version(self) -> str:
        return "v3"

__all__ = ["Metrics", "MetricsV3"] 