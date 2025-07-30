from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    PositiveInt,
    constr,
    field_validator,
)


class SDKBaseModel(BaseModel):
    class Config:
        extra = "forbid"

    def to_json(self, **kwargs: dict[str, object]) -> str:
        """
        Return a JSON string representation of the model.
        Ensures valid JSON output regardless of Pydantic version.
        Always excludes None fields by default.
        """
        kwargs.setdefault("exclude_none", True)
        return self.model_dump_json(**kwargs)

    def to_dict(self, **kwargs: dict[str, object]) -> dict:
        """
        Return a dict representation of the model, always excluding None fields by default.
        """
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)

    @classmethod
    def validate_score_range(cls, v: float | int | list | dict, min_value: float, max_value: float, label: str) -> object:
        if isinstance(v, float) or isinstance(v, int):
            if not (min_value <= v <= max_value):
                raise ValueError(f"{label} score {v} must be between {min_value} and {max_value}")
        elif isinstance(v, list):
            for s in v:
                if not (min_value <= s <= max_value):
                    raise ValueError(f"{label} score {s} must be between {min_value} and {max_value}")
        elif isinstance(v, dict):
            for k, s in v.items():
                if not (min_value <= s <= max_value):
                    raise ValueError(f"{label} score for '{k}' was {s}, must be between {min_value} and {max_value}")
        return v

    @staticmethod
    def format_validation_error(model_cls: type, validation_error: Exception) -> str:
        """
        Format a Pydantic ValidationError into a user-friendly error message using field types and descriptions.
        Distinguishes between missing and invalid arguments, and sets the error prefix accordingly.
        """
        errors = validation_error.errors()
        model_fields = getattr(model_cls, "model_fields", getattr(model_cls, "__fields__", {}))
        messages = []
        error_types = set()
        def get_type_str(field_type: type) -> str:
            origin = getattr(field_type, "__origin__", None)
            args = getattr(field_type, "__args__", None)
            if origin and args:
                origin_name = getattr(origin, "__name__", str(origin))
                args_str = ", ".join(get_type_str(a) for a in args)
                return f"{origin_name}[{args_str}]"
            return getattr(field_type, "__name__", str(field_type))
        for err in errors:
            loc = err.get("loc", [])
            field = loc[0] if loc else None
            actual_value = err.get("input", None)
            actual_type = type(actual_value).__name__ if actual_value is not None else "NoneType"
            err_type = err.get("type", "")
            if err_type.startswith("missing"):
                error_types.add("missing")
            else:
                error_types.add("invalid")
            if field and field in model_fields:
                field_info = model_fields[field]
                field_type = getattr(field_info, "annotation", getattr(field_info, "type_", None))
                type_str = get_type_str(field_type) if field_type else "unknown"
                if err_type.startswith("missing"):
                    messages.append(f"'{field}' (missing required argument, expected type: {type_str})")
                else:
                    messages.append(
                        f"'{field}' (invalid value: expected type: {type_str}, got: {actual_type} [value: {actual_value!r}])"
                    )
            elif field:
                if err_type.startswith("missing"):
                    messages.append(f"'{field}' (missing required argument)")
                else:
                    messages.append(f"'{field}' (invalid value: got: {actual_type} [value: {actual_value!r}])")
            else:
                messages.append(str(err))
        model_name = getattr(model_cls, "__name__", str(model_cls))
        if error_types == {"missing"}:
            prefix = "Missing required arguments"
        elif error_types == {"invalid"}:
            prefix = "Invalid arguments"
        else:
            prefix = "Invalid or missing arguments"
        return f"Error in '{model_name}': {prefix}: {', '.join(messages)}. Refer to the documentation: https://trustwiseai.github.io/tw-docs/docs/intro"

class Fact(SDKBaseModel):
    """
    A fact extracted from a response with its verification status.
    :param statement: The fact statement text.
    :param label: The label for the fact.
    :param prob: The probability/confidence for the fact.
    :param sentence_span: The character span of the statement in the response.
    """
    statement: str
    label: str
    prob: float
    sentence_span: list[int]

Facts = list[Fact]

class FaithfulnessResponse(SDKBaseModel):
    """
    Response type for faithfulness evaluation.
    :param score: The faithfulness score.
    :param facts: List of facts extracted from the response.
    """
    score: float = Field(..., ge=0, le=100, description="Faithfulness score (0-100)")
    facts: Facts
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Faithfulness")

class AnswerRelevancyResponse(SDKBaseModel):
    """
    Response type for answer relevancy evaluation.

    :param score: The answer relevancy score.
    :param generated_question: The generated question for evaluation.
    """
    score: float = Field(..., ge=0, le=100, description="Answer relevancy score (0-100)")
    generated_question: str
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Answer relevancy")

class ContextNode(SDKBaseModel):
    """
    A single context node with its metadata.

    :param node_id: The unique identifier for the context node.
    :param node_score: The score associated with the node.
    :param node_text: The text content of the node.
    """
    node_id: str
    node_score: float
    node_text: str

# Define Context as a list of ContextNode (Pydantic model)
Context = list[ContextNode]
"""A list of ContextNode objects representing the context for evaluation."""

class ContextRelevancyRequest(SDKBaseModel):
    """
    Request type for context relevancy evaluation.
    :param query: The input query string.
    :param context: The context information (required).
    :param response: The response to evaluate.
    """
    query: str
    context: Context
    response: str

class ContextRelevancyResponse(SDKBaseModel):
    """
    Response type for context relevancy evaluation.
    :param score: The context relevancy score.
    :param topics: List of topics identified.
    :param scores: List of scores for each topic.
    """
    score: float = Field(..., ge=0, le=100, description="Context relevancy score (0-100)")
    topics: list[str]
    scores: list[float]
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Context relevancy")
    @field_validator("scores", mode="before")
    @classmethod
    def check_scores(cls, v: list[float]) -> list[float]:
        return cls.validate_score_range(v, 0, 100, "Context relevancy")

class SummarizationRequest(SDKBaseModel):
    """
    Request type for summarization evaluation.
    :param query: The input query string.
    :param response: The response to evaluate.
    :param context: The context information (required).
    """
    query: str
    response: str
    context: Context

class SummarizationResponse(SDKBaseModel):
    """
    Response type for summarization quality evaluation.
    :param score: The summarization score.
    """
    score: float = Field(..., ge=0, le=100, description="Summarization score (0-100)")
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Summarization")

class PIIEntity(SDKBaseModel):
    """
    A detected piece of personally identifiable information.
    :param interval: The [start, end] indices of the PII in the text.
    :param string: The detected PII string.
    :param category: The PII category.
    """
    interval: list[int]
    string: str
    category: str

class PIIRequest(SDKBaseModel):
    """
    Request type for PII detection.
    :param text: The text to evaluate.
    :param allowlist: List of allowed PII categories.
    :param blocklist: List of blocked PII categories.
    """
    text: str
    allowlist: list[str]
    blocklist: list[str]

class PIIResponse(SDKBaseModel):
    """
    Response type for PII detection.
    :param identified_pii: List of detected PII entities.
    """
    identified_pii: list[PIIEntity]

class PromptInjectionRequest(SDKBaseModel):
    """
    Request type for prompt injection detection.
    :param query: The input query string.
    :param response: The response to evaluate.
    :param context: The context information (required).
    """
    query: str
    response: str
    context: Context = Field(..., min_items=1, description="A non-empty list of ContextNode objects.")

class PromptInjectionResponse(SDKBaseModel):
    """
    Response type for prompt injection detection.
    :param score: The prompt injection score.
    """
    score: float = Field(..., ge=0, le=100, description="Prompt injection score (0-100)")
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Prompt injection")

class ClarityRequest(SDKBaseModel):
    """
    Request type for clarity evaluation.
    :param query: The input query string.
    :param response: The response to evaluate.
    """
    query: str
    response: str

class ClarityResponse(SDKBaseModel):
    """
    Response type for clarity evaluation.
    :param score: The overall clarity score.
    """
    score: float = Field(..., ge=0, le=100, description="Clarity score (0-100)")
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Clarity")

class HelpfulnessRequest(SDKBaseModel):
    """
    Request type for helpfulness evaluation.
    :param query: The input query string.
    :param response: The response to evaluate.
    """
    query: str
    response: str

class HelpfulnessResponse(SDKBaseModel):
    """
    Response type for helpfulness evaluation.
    :param score: The overall helpfulness score.
    """
    score: float = Field(..., ge=0, le=100, description="Helpfulness score (0-100)")
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Helpfulness")

class FormalityRequest(SDKBaseModel):
    """
    Request type for formality evaluation.
    :param response: The response to evaluate.
    """
    response: str

class FormalityResponse(SDKBaseModel):
    """
    Response type for formality evaluation.
    :param score: The overall formality score.
    :param sentences: List of sentences analyzed.
    :param scores: List of scores for each sentence.
    """
    score: float = Field(..., ge=0, le=100, description="Formality score (0-100)")
    sentences: list[str]
    scores: list[float]
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Formality")
    @field_validator("scores", mode="before")
    @classmethod
    def check_scores(cls, v: list[float]) -> list[float]:
        return cls.validate_score_range(v, 0, 100, "Formality")

class SimplicityResponse(SDKBaseModel):
    """
    Response type for simplicity evaluation.
    :param score: The overall simplicity score (percentage).
    """
    score: float = Field(..., ge=0, le=100, description="Simplicity score (0-100)")
    @field_validator("score", mode="before")
    @classmethod
    def check_score(cls, v: float) -> float:
        return cls.validate_score_range(v, 0, 100, "Simplicity")

class SensitivityResponse(SDKBaseModel):
    """
    Response type for sensitivity evaluation.
    :param scores: Mapping of topic to sensitivity score.
    """
    scores: dict[str, float]
    @field_validator("scores", mode="before")
    @classmethod
    def check_scores(cls, v: dict[str, float]) -> dict[str, float]:
        return cls.validate_score_range(v, 0, 100, "Sensitivity")

class ToxicityResponse(SDKBaseModel):
    """
    Response type for toxicity evaluation.
    :param labels: List of toxicity category labels.
    :param scores: List of scores for each label (0-100).
    """
    labels: list[str]
    scores: list[float]
    @field_validator("scores", mode="before")
    @classmethod
    def check_scores(cls, v: list[float]) -> list[float]:
        return cls.validate_score_range(v, 0, 100, "Toxicity")

class ToneResponse(SDKBaseModel):
    """
    Response type for tone evaluation.
    :param labels: List of detected tone labels.
    :param scores: List of scores for each label.
    """
    labels: list[str]
    scores: list[float]
    @field_validator("scores", mode="before")
    @classmethod
    def check_scores(cls, v: list[float]) -> list[float]:
        return cls.validate_score_range(v, 0, 100, "Tone")

class CostResponse(SDKBaseModel):
    """
    Response type for cost evaluation.
    :param cost_estimate_per_run: Estimated cost per run.
    :param total_project_cost_estimate: Total estimated cost for the project.
    """
    cost_estimate_per_run: float
    total_project_cost_estimate: float

class CarbonResponse(SDKBaseModel):
    """
    Response type for carbon emissions evaluation.
    :param carbon_emitted: Estimated carbon emitted (kg CO2e).
    :param sci_per_api_call: SCI per API call.
    :param sci_per_10k_calls: SCI per 10,000 calls.
    """
    carbon_emitted: float
    sci_per_api_call: float
    sci_per_10k_calls: float

class FaithfulnessRequest(SDKBaseModel):
    """
    Request type for faithfulness evaluation.
    :param query: The input query string.
    :param response: The response to evaluate.
    :param context: The context information (required).
    """
    query: str
    response: str
    context: Context

class AnswerRelevancyRequest(SDKBaseModel):
    """
    Request type for answer relevancy evaluation.
    :param query: The input query string.
    :param response: The response to evaluate.
    :param context: The context information (required).
    """
    query: str
    response: str
    context: Context

class SimplicityRequest(SDKBaseModel):
    """
    Request type for simplicity evaluation.
    :param response: The response to evaluate.
    """
    response: str

class SensitivityRequest(SDKBaseModel):
    """
    Request type for sensitivity evaluation.
    :param response: The response to evaluate.
    :param topics: List of topics to check for sensitivity.
    :param query: The input query string (optional).
    """
    response: str
    topics: list[str]
    query: str | None = None

class ToxicityRequest(SDKBaseModel):
    """
    Request type for toxicity evaluation.
    :param query: The input query string.
    :param response: The response to evaluate.
    """
    query: str
    response: str

class ToneRequest(SDKBaseModel):
    """
    Request type for tone evaluation.
    :param response: The response to evaluate.
    """
    response: str

class CostRequest(SDKBaseModel):
    """
    Request type for cost evaluation.
    :param model_name: Name of the model (non-empty string).
    :param model_type: Type of the model (must be 'LLM' or 'Reranker').
    :param model_provider: Provider of the model (non-empty string).
    :param number_of_queries: Number of queries to estimate cost for (> 0).
    :param total_prompt_tokens: Total prompt tokens (> 0).
    :param total_completion_tokens: Total completion tokens (> 0).
    :param total_tokens: Total tokens (optional, > 0 if provided).
    :param instance_type: Instance type (optional).
    :param average_latency: Average latency (optional, > 0 if provided).
    """
    model_name: constr(strip_whitespace=True, min_length=1) = Field(..., description="Model name must be a non-empty string.")
    model_type: Literal["LLM", "Reranker"] = Field(..., description="Model type must be 'LLM' or 'Reranker'.")
    model_provider: constr(strip_whitespace=True, min_length=1) = Field(..., description="Model provider must be a non-empty string.")
    number_of_queries: PositiveInt = Field(..., description="Number of queries must be > 0.")
    total_prompt_tokens: PositiveInt = Field(..., description="Total number of prompt tokens (must be > 0).")
    total_completion_tokens: PositiveInt = Field(..., description="Total number of completion tokens (must be > 0).")
    total_tokens: PositiveInt | None = Field(None, description="Total tokens (optional, must be > 0 if provided).")
    instance_type: str | None = Field(None, description="Instance type required for Hugging Face models.")
    average_latency: PositiveFloat | None = Field(None, description="Optional: Average latency in milliseconds, must be > 0 if provided.")

class CarbonRequest(SDKBaseModel):
    """
    Request type for carbon evaluation.
    :param processor_name: Name of the processor.
    :param provider_name: Name of the provider.
    :param provider_region: Region of the provider.
    :param instance_type: Instance type.
    :param average_latency: Average latency (ms).
    """
    processor_name: str
    provider_name: str
    provider_region: str
    instance_type: str
    average_latency: int

class GuardrailResponse(SDKBaseModel):
    """
    Response type for guardrail evaluation.
    :param passed: Whether all metrics passed.
    :param blocked: Whether the response is blocked due to failure.
    :param results: Dictionary of metric results, each containing 'passed' and 'result'.
    """
    passed: bool
    blocked: bool
    results: dict

    def to_json(self, **kwargs: dict[str, object]) -> str:
        """
        Return a JSON string representation of the guardrail evaluation, recursively serializing all nested SDK types.
        Use this for logging, API responses, or storage.
        """
        def serialize(obj: object) -> object:
            if hasattr(obj, "to_json"):
                return obj.model_dump()
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            return obj
        data = {
            "passed": self.passed,
            "blocked": self.blocked,
            "results": serialize(self.results)
        }
        import json
        return json.dumps(data, **kwargs)

    def to_dict(self) -> dict:
        """
        Return a Python dict representation of the guardrail evaluation, recursively serializing all nested SDK types.
        Use this for programmatic access, further processing, or conversion to JSON via json.dumps().
        """
        def serialize(obj: object) -> object:
            if hasattr(obj, "to_json"):
                return obj.model_dump()
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            return obj
        return {
            "passed": self.passed,
            "blocked": self.blocked,
            "results": serialize(self.results)
        } 
