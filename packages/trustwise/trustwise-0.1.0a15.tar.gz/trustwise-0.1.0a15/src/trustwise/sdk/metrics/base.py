import logging
from abc import ABC, abstractmethod
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)
from urllib.parse import urljoin

from pydantic import ValidationError

from trustwise.sdk.exceptions import TrustwiseValidationError
from trustwise.sdk.types import (
    AnswerRelevancyRequest,
    AnswerRelevancyResponse,
    ClarityRequest,
    ClarityResponse,
    ContextRelevancyRequest,
    ContextRelevancyResponse,
    FaithfulnessRequest,
    FaithfulnessResponse,
    FormalityRequest,
    FormalityResponse,
    HelpfulnessRequest,
    HelpfulnessResponse,
    PIIRequest,
    PIIResponse,
    PromptInjectionRequest,
    PromptInjectionResponse,
    SDKBaseModel,
    SensitivityRequest,
    SensitivityResponse,
    SimplicityRequest,
    SimplicityResponse,
    SummarizationRequest,
    SummarizationResponse,
    ToxicityRequest,
    ToxicityResponse,
)

logger = logging.getLogger(__name__)

# Generic type variables for request and response
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


@runtime_checkable
class MetricProtocol(Protocol[TRequest, TResponse]):
    """Protocol defining the interface for all metrics."""
    def evaluate(self, request: TRequest) -> TResponse:
        """Evaluate the metric with a specific request."""
        ...
    
    def batch_evaluate(self, inputs: list[TRequest]) -> list[TResponse]:
        """Evaluate multiple inputs in a single request."""
        ...
    
    def explain(self, *args, **kwargs) -> dict[str, Any]:
        """Get detailed explanation of the evaluation."""
        ...


class BaseMetric(ABC, Generic[TRequest, TResponse]):
    """Base class for all metrics."""
    
    def __init__(self, client: object, base_url: str, version: str) -> None:
        self.client = client
        self.base_url = base_url
        self.version = version
        logger.debug("Initialized %s with base_url: %s, version: %s", 
                    self.__class__.__name__, base_url, version)

    def _get_endpoint_url(self, endpoint: str) -> str:
        """Get the full URL for an endpoint."""
        url = urljoin(str(self.base_url) + "/", endpoint)
        logger.debug("Constructed URL for endpoint %s: %s", endpoint, url)
        return url

    @abstractmethod
    def evaluate(self, request: TRequest) -> TResponse:
        """Evaluate the metric. Must be implemented by concrete classes."""
        pass

    def batch_evaluate(self, inputs: list[TRequest]) -> list[TResponse]:
        """Evaluate multiple inputs in a single request. Optional implementation."""
        raise NotImplementedError("Batch evaluation not supported for this metric")

    def explain(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Get detailed explanation of the evaluation. Optional implementation."""
        raise NotImplementedError("Explanation not supported for this metric")

    def _post(self, endpoint: str, data: object) -> object:
        """Make a POST request to the metric endpoint."""
        return self.client._post(self._get_endpoint_url(endpoint), data)

    @staticmethod
    def validate_request_model(model_cls: type, **kwargs: Any) -> object:
        """
        Standardized Trustwise validation for all metric request models.
        Usage: req = BaseMetric.validate_request_model(RequestModel, **kwargs)
        Raises TrustwiseValidationError with a formatted message on error.
        """
        try:
            return model_cls(**kwargs)
        except ValidationError as ve:
            raise TrustwiseValidationError(SDKBaseModel.format_validation_error(model_cls, ve)) from ve
        except TypeError as te:
            # Detect missing required arguments
            import inspect
            sig = inspect.signature(model_cls)
            missing_args = []
            for name, param in sig.parameters.items():
                if param.default is param.empty and name not in kwargs:
                    missing_args.append(name)
            if missing_args:
                class DummyValidationError(Exception):
                    def errors(self) -> list:
                        return [
                            {"loc": [arg], "msg": "field required"} for arg in missing_args
                        ]
                ve = DummyValidationError()
                raise TrustwiseValidationError(SDKBaseModel.format_validation_error(model_cls, ve)) from te
            else:
                raise


class MetricEvaluator(BaseMetric, Generic[TRequest, TResponse]):
    """Base class for all metric evaluations with typed request/response."""
    
    def evaluate(self, request: TRequest) -> TResponse:
        """Evaluate the metric with a specific request type."""
        return self.client._post(
            endpoint=f"{self.base_url}/{self._get_endpoint_name()}",
            data=request
        )
    
    def batch_evaluate(self, inputs: list[TRequest]) -> list[TResponse]:
        """Evaluate multiple inputs in a single request."""
        raise NotImplementedError("Batch evaluation not yet supported")
    
    def explain(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Get detailed explanation of the evaluation."""
        raise NotImplementedError("Explanation not yet supported")
    
    def _get_endpoint_name(self) -> str:
        """Get the endpoint name for this metric. Override in subclasses."""
        # Default implementation strips 'Metric' from the class name and converts to snake_case
        class_name = self.__class__.__name__
        metric_name = class_name[:-6] if class_name.endswith("Metric") else class_name
        return "".join(["_" + c.lower() if c.isupper() else c for c in metric_name]).lstrip("_")


class MetricRegistry:
    """Registry for mapping request types to metric handlers."""
    
    def __init__(self) -> None:
        self._registry: dict[type, object] = {}
    
    def register(self, request_type: type, handler: object) -> None:
        """Register a handler for a specific request type."""
        self._registry[request_type] = handler
    
    def get_handler(self, request: object) -> object | None:
        """Get the appropriate handler for a given request."""
        request_type = type(request)
        return self._registry.get(request_type)


class BaseSafetyMetric(BaseMetric[Any, Any]):
    """Base class for safety metrics."""
    
    def __init__(self, client: object, base_url: str, version: str) -> None:
        super().__init__(client, base_url, version)
        self._registry = MetricRegistry()
        self._initialize_registry()
    
    def _initialize_registry(self) -> None:
        """Initialize the registry with available metrics. Override in concrete classes."""
        pass
        
    def evaluate(self, request: object) -> object:
        """Evaluate the safety metrics based on request type."""
        handler = self._registry.get_handler(request)
        if handler:
            return handler(request)
        else:
            raise ValueError(f"Unsupported request type: {type(request)}")

    def batch_evaluate(self, inputs: list[Any]) -> list[Any]:
        """Evaluate multiple inputs in a single request."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Get detailed explanation of the evaluation."""
        raise NotImplementedError("Explanation not yet supported")
    
    def faithfulness(self, request: FaithfulnessRequest) -> FaithfulnessResponse:
        """Evaluate faithfulness of a response."""
        return self.client._post(self._get_endpoint_url("faithfulness"), request)
    
    def context_relevancy(self, request: ContextRelevancyRequest) -> ContextRelevancyResponse:
        """Evaluate context relevancy of a response."""
        return self.client._post(self._get_endpoint_url("context_relevancy"), request)
    
    def answer_relevancy(self, request: AnswerRelevancyRequest) -> AnswerRelevancyResponse:
        """Evaluate answer relevancy of a response."""
        return self.client._post(self._get_endpoint_url("answer_relevancy"), request)
    
    def summarization(self, request: SummarizationRequest) -> SummarizationResponse:
        """Evaluate summarization quality."""
        return self.client._post(self._get_endpoint_url("summarization"), request)
    
    def clarity(self, request: ClarityRequest) -> ClarityResponse:
        """Evaluate clarity of a response."""
        return self.client._post(self._get_endpoint_url("clarity"), request)
    
    def helpfulness(self, request: HelpfulnessRequest) -> HelpfulnessResponse:
        """Evaluate helpfulness of a response."""
        return self.client._post(self._get_endpoint_url("helpfulness"), request)

    def pii(self, request: PIIRequest) -> PIIResponse:
        """Evaluate text for PII content."""
        if not request.text or not isinstance(request.text, str):
            raise ValueError("Text must be a non-empty string")
            
        return self.client._post(self._get_endpoint_url("pii"), request)

    def prompt_injection(self, request: PromptInjectionRequest) -> PromptInjectionResponse:
        """Evaluate text for prompt injection attempts."""
        if not request.query or not isinstance(request.query, str):
            raise ValueError("Query must be a non-empty string")
            
        return self.client._post(self._get_endpoint_url("prompt_injection"), request)


class BaseAlignmentMetric(BaseMetric[Any, Any]):
    """Base class for alignment metrics."""
    
    def __init__(self, client: object, base_url: str, version: str) -> None:
        super().__init__(client, base_url, version)
        self._registry = MetricRegistry()
        # Do NOT call self._initialize_registry() here; let subclasses call it after their own init
    
    def evaluate(self, request: object) -> object:
        """Evaluate the alignment metrics based on request type."""
        handler = self._registry.get_handler(request)
        if handler:
            return handler(request)
        else:
            # Default to clarity if not found
            if isinstance(request, ClarityRequest):
                return self.clarity(request)
            else:
                raise ValueError(f"Unsupported request type: {type(request)}")

    def batch_evaluate(self, inputs: list[Any]) -> list[Any]:
        """Evaluate multiple inputs in a single request."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Get detailed explanation of the evaluation."""
        raise NotImplementedError("Explanation not yet supported")
    
    def clarity(self, request: ClarityRequest) -> ClarityResponse:
        """Evaluate clarity of a response."""
        return self.client._post(self._get_endpoint_url("clarity"), request)
    
    def helpfulness(self, request: HelpfulnessRequest) -> HelpfulnessResponse:
        """Evaluate helpfulness of a response."""
        return self.client._post(self._get_endpoint_url("helpfulness"), request)
    
    def formality(self, request: FormalityRequest) -> FormalityResponse:
        """Evaluate formality of a response."""
        return self.client._post(self._get_endpoint_url("formality"), request)
    
    def simplicity(self, request: SimplicityRequest) -> SimplicityResponse:
        """Evaluate simplicity of a response."""
        return self.client._post(self._get_endpoint_url("simplicity"), request)
    
    def sensitivity(self, request: SensitivityRequest) -> SensitivityResponse:
        """Evaluate sensitivity regarding specific topics."""
        return self.client._post(self._get_endpoint_url("sensitivity"), request)
    
    def toxicity(self, request: ToxicityRequest) -> ToxicityResponse:
        """Evaluate toxicity."""
        return self.client._post(self._get_endpoint_url("toxicity"), request)


class BasePerformanceMetric(BaseMetric[dict[str, Any], dict[str, Any]]):
    """Base class for performance metrics."""
    
    def __init__(self, client: object, base_url: str, version: str) -> None:
        super().__init__(client, base_url, version)
        self._registry = MetricRegistry()
        # Do NOT call self._initialize_registry() here; let subclasses call it after their own init
    
    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate the performance metrics."""
        # Default to using cost metric with the request
        return self.cost(**request)

    def batch_evaluate(self, inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Evaluate multiple inputs in a single request."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Get detailed explanation of the evaluation."""
        raise NotImplementedError("Explanation not yet supported")
    
    def cost(
        self,
        total_prompt_tokens: int,
        total_completion_tokens: int,
        model_name: str,
        model_provider: str,
        average_latency: int,
        number_of_queries: int,
        instance_type: str
    ) -> dict[str, Any]:
        """Evaluate cost metrics."""
        data = {
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "model_name": model_name,
            "model_provider": model_provider,
            "average_latency": average_latency,
            "number_of_queries": number_of_queries,
            "instance_type": instance_type
        }
        return self.client._post(self._get_endpoint_url("cost"), data)
    
    def carbon(
        self,
        processor_name: str,
        provider_name: str,
        provider_region: str,
        instance_type: str,
        average_latency: int
    ) -> dict[str, Any]:
        """Evaluate carbon metrics."""
        data = {
            "processor_name": processor_name,
            "provider_name": provider_name,
            "provider_region": provider_region,
            "instance_type": instance_type,
            "average_latency": average_latency
        }
        return self.client._post(self._get_endpoint_url("carbon"), data) 