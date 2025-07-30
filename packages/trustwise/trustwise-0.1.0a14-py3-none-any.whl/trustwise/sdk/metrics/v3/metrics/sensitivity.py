from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import SensitivityRequest, SensitivityResponse


class SensitivityMetric:
    """Sensitivity metric for evaluating response sensitivity."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_alignment_url("v1")

    def evaluate(
        self,
        *,
        response: str | None = None,
        topics: list | None = None,
        query: str | None = None,
        **kwargs
    ) -> SensitivityResponse:
        """
        Evaluate the sensitivity of a response.

        Args:
            response: The response string (required)
            topics: List of topics to check for sensitivity (required)
            query: The input query string (optional)

        Returns:
            SensitivityResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(SensitivityRequest, response=response, topics=topics, query=query, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/sensitivity",
            data=req.to_dict()
        )
        return SensitivityResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[SensitivityRequest]
    ) -> list[SensitivityResponse]:
        """Evaluate multiple inputs for sensitivity."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        response: str,
        topics: list[str],
        query: str | None = None,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the sensitivity evaluation."""
        # req = SensitivityRequest(response=response, topics=topics, query=query)
        raise NotImplementedError("Explanation not yet supported") 