from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import SimplicityRequest, SimplicityResponse


class SimplicityMetric:
    """Simplicity metric for evaluating response simplicity."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_alignment_url("v1")

    def evaluate(
        self,
        *,
        response: str | None = None,
        **kwargs
    ) -> SimplicityResponse:
        """
        Evaluate the simplicity of a response.

        Args:
            response: The response string (required)

        Returns:
            SimplicityResponse containing the evaluation results
        """
        req = BaseMetric.validate_request_model(SimplicityRequest, response=response, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/simplicity",
            data=req.to_dict()
        )
        return SimplicityResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[SimplicityRequest]
    ) -> list[SimplicityResponse]:
        """Evaluate multiple inputs for simplicity."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        response: str,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the simplicity evaluation."""
        # req = SimplicityRequest(response=response)
        raise NotImplementedError("Explanation not yet supported") 