from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import ClarityRequest, ClarityResponse


class ClarityMetric:
    """Clarity metric for evaluating response clarity."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_alignment_url("v1")

    def evaluate(
        self,
        *,
        query: str | None = None,
        response: str | None = None,
        **kwargs
    ) -> ClarityResponse:
        """
        Evaluate the clarity of a response to the query.

        Args:
            query: The query string (required)
            response: The response string (required)

        Returns:
            ClarityResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(ClarityRequest, query=query, response=response, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/clarity",
            data=req.to_dict()
        )
        return ClarityResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[ClarityRequest]
    ) -> list[ClarityResponse]:
        """Evaluate multiple inputs for clarity."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        query: str,
        response: str,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the clarity evaluation."""
        # req = ClarityRequest(query=query, response=response)
        raise NotImplementedError("Explanation not yet supported") 