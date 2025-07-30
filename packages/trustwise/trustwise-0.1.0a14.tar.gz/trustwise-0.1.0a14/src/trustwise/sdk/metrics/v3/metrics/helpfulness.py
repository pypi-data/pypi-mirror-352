from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import HelpfulnessRequest, HelpfulnessResponse


class HelpfulnessMetric:
    """Helpfulness metric for evaluating response helpfulness."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_alignment_url("v1")

    def evaluate(
        self,
        *,
        query: str | None = None,
        response: str | None = None,
        **kwargs
    ) -> HelpfulnessResponse:
        """
        Evaluate the helpfulness of a response to the query.

        Args:
            query: The query string (required)
            response: The response string (required)

        Returns:
            HelpfulnessResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(HelpfulnessRequest, query=query, response=response, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/helpfulness",
            data=req.to_dict()
        )
        return HelpfulnessResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[HelpfulnessRequest]
    ) -> list[HelpfulnessResponse]:
        """Evaluate multiple inputs for helpfulness."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        query: str,
        response: str,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the helpfulness evaluation."""
        # req = HelpfulnessRequest(query=query, response=response)
        raise NotImplementedError("Explanation not yet supported") 