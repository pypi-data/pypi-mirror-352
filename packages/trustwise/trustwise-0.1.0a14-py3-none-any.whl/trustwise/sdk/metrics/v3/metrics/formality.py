from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import FormalityRequest, FormalityResponse


class FormalityMetric:
    """Formality metric for evaluating response formality."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_alignment_url("v1")

    def evaluate(
        self,
        *,
        response: str | None = None,
        **kwargs
    ) -> FormalityResponse:
        """
        Evaluate the formality of a response.

        Args:
            response: The response string (required)

        Returns:
            FormalityResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(FormalityRequest, response=response, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/formality",
            data=req.to_dict()
        )
        return FormalityResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[FormalityRequest]
    ) -> list[FormalityResponse]:
        """Evaluate multiple inputs for formality."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        response: str,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the formality evaluation."""
        # req = FormalityRequest(response=response)
        raise NotImplementedError("Explanation not yet supported") 