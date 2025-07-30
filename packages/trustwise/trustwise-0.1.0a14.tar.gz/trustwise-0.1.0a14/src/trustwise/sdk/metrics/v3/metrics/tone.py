from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import ToneRequest, ToneResponse


class ToneMetric:
    """Tone metric for evaluating response tone."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_alignment_url("v1")

    def evaluate(
        self,
        *,
        response: str | None = None,
        **kwargs
    ) -> ToneResponse:
        """
        Evaluate the tone of a response.

        Args:
            response: The response string (required)

        Returns:
            ToneResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(ToneRequest, response=response, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/tone",
            data=req.to_dict()
        )
        return ToneResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[ToneRequest]
    ) -> list[ToneResponse]:
        """Evaluate multiple inputs for tone."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        response: str,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the tone evaluation."""
        # req = ToneRequest(response=response)
        raise NotImplementedError("Explanation not yet supported") 