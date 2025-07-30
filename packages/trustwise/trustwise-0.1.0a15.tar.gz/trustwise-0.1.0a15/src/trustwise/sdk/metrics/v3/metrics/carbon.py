from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import CarbonRequest, CarbonResponse


class CarbonMetric:
    """Carbon emissions metrics evaluator."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_performance_url("v1")

    def evaluate(
        self,
        *,
        processor_name: str | None = None,
        provider_name: str | None = None,
        provider_region: str | None = None,
        instance_type: str | None = None,
        average_latency: int | None = None,
        **kwargs
    ) -> CarbonResponse:
        """
        Evaluate carbon metrics.
        All arguments are required except those marked optional.
        """
        req = BaseMetric.validate_request_model(
            CarbonRequest,
            processor_name=processor_name,
            provider_name=provider_name,
            provider_region=provider_region,
            instance_type=instance_type,
            average_latency=average_latency,
            **kwargs
        )
        result = self.client._post(
            endpoint=f"{self.base_url}/carbon",
            data=req.to_dict()
        )
        return CarbonResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[CarbonRequest]
    ) -> list[CarbonResponse]:
        """Evaluate multiple inputs for carbon."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        processor_name: str | None = None,
        provider_name: str | None = None,
        provider_region: str | None = None,
        instance_type: str | None = None,
        average_latency: int | None = None,
        **kwargs
    ) -> dict:
        """Get detailed explanation of the carbon evaluation."""
        # req = CarbonRequest(
        #     processor_name=processor_name,
        #     provider_name=provider_name,
        #     provider_region=provider_region,
        #     instance_type=instance_type,
        #     average_latency=average_latency
        # )
        raise NotImplementedError("Explanation not yet supported") 