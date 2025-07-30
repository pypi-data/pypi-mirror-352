from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.types import (
    Context,
    PromptInjectionRequest,
    PromptInjectionResponse,
)


class PromptInjectionMetric:
    """Prompt injection detection metric."""
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_safety_url("v3")
    
    def evaluate(
        self,
        *,
        query: str,
        response: str,
        context: Context,
        **kwargs
    ) -> PromptInjectionResponse:
        """
        Evaluate the prompt injection risk of a response.

        Args:
            query: The query string (required)
            response: The response string (required)
            context: The context information (required)

        Returns:
            PromptInjectionResponse containing the evaluation results
        """
        req = PromptInjectionRequest(query=query, response=response, context=context, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/prompt_injection",
            data=req.to_dict()
        )
        return PromptInjectionResponse(**result)
    
    def batch_evaluate(
        self,
        inputs: list[PromptInjectionRequest]
    ) -> list[PromptInjectionResponse]:
        """Evaluate multiple inputs for prompt injection attempts."""
        raise NotImplementedError("Batch evaluation not yet supported")
    
    def explain(
        self,
        *,
        query: str,
        response: str,
        context: Context,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the prompt injection detection."""
        # req = PromptInjectionRequest(query=query, response=response, context=context)
        raise NotImplementedError("Explanation not yet supported") 