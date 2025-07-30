from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import (
    Context,
    FaithfulnessRequest,
    FaithfulnessResponse,
)


class FaithfulnessMetric:
    """Faithfulness metric for evaluating response accuracy against context."""
    
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
    ) -> FaithfulnessResponse:
        """
        Evaluate the faithfulness of a response against its context.

        Args:
            query: The query string (required)
            response: The response string (required)
            context: The context information (required)

        Returns:
            FaithfulnessResponse containing the evaluation results

        Raises:
            TrustwiseValidationError: If not all of query, response, and context are provided
        """
        req = BaseMetric.validate_request_model(FaithfulnessRequest, query=query, response=response, context=context, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/faithfulness",
            data=req.to_dict()
        )
        return FaithfulnessResponse(**result)
    
    def batch_evaluate(
        self,
        inputs: list[FaithfulnessRequest]
    ) -> list[FaithfulnessResponse]:
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
        """Get detailed explanation of the evaluation. Context is required."""
        # req = FaithfulnessRequest(query=query, response=response, context=context)
        raise NotImplementedError("Explanation not yet supported") 