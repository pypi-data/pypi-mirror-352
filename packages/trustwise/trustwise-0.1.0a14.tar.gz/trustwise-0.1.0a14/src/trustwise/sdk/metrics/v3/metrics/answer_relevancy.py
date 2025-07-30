from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import (
    AnswerRelevancyRequest,
    AnswerRelevancyResponse,
    Context,
)


class AnswerRelevancyMetric:
    """Answer relevancy metric for evaluating response relevance to query."""
    
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
    ) -> AnswerRelevancyResponse:
        """
        Evaluate the relevancy of a response to the query.

        Args:
            query: The query string (required)
            response: The response string (required)
            context: The context information (required)

        Returns:
            AnswerRelevancyResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(AnswerRelevancyRequest, query=query, response=response, context=context, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/answer_relevancy",
            data=req.to_dict()
        )
        return AnswerRelevancyResponse(**result)
    
    def batch_evaluate(
        self,
        inputs: list[AnswerRelevancyRequest]
    ) -> list[AnswerRelevancyResponse]:
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
        # req = AnswerRelevancyRequest(query=query, response=response, context=context)
        raise NotImplementedError("Explanation not yet supported") 