from typing import Any

from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import Context, SummarizationRequest, SummarizationResponse


class SummarizationMetric:
    """Summarization metric for evaluating response summarization quality."""
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_safety_url("v3")
    
    def evaluate(
        self,
        *,
        query: str | None = None,
        response: str | None = None,
        context: Context | None = None,
        **kwargs
    ) -> SummarizationResponse:
        """
        Evaluate the quality of a summarization.

        Args:
            query: The query string (required)
            response: The response string (required)
            context: The context information (required)

        Returns:
            SummarizationResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(SummarizationRequest, query=query, response=response, context=context, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/summarization",
            data=req.to_dict()
        )
        return SummarizationResponse(**result)
    
    def batch_evaluate(
        self,
        inputs: list[dict[str, Any]]
    ) -> list[SummarizationResponse]:
        """Evaluate multiple inputs in a single request."""
        raise NotImplementedError("Batch evaluation not yet supported")
    
    def explain(
        self,
        *,
        query: str,
        response: str,
        context: Context,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the evaluation."""
        # req = SummarizationRequest(query=query, response=response, context=context)
        raise NotImplementedError("Explanation not yet supported") 