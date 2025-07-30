from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.types import CostRequest, CostResponse


class CostMetric:
    """Cost metrics evaluator."""
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_performance_url("v1")

    def evaluate(
        self,
        *,
        model_name: str | None = None,
        model_type: str | None = None,
        model_provider: str | None = None,
        number_of_queries: int | None = None,
        total_prompt_tokens: int | None = None,
        total_completion_tokens: int | None = None,
        total_tokens: int | None = None,
        instance_type: str | None = None,
        average_latency: float | None = None,
        **kwargs
    ) -> CostResponse:
        """
        Evaluate cost metrics.
        All arguments are required except those marked optional.
        """
        req = BaseMetric.validate_request_model(
            CostRequest,
            model_name=model_name,
            model_type=model_type,
            model_provider=model_provider,
            number_of_queries=number_of_queries,
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            instance_type=instance_type,
            average_latency=average_latency,
            **kwargs
        )
        result = self.client._post(
            endpoint=f"{self.base_url}/cost",
            data=req.to_dict()
        )
        return CostResponse(**result)

    def batch_evaluate(
        self,
        inputs: list[CostRequest]
    ) -> list[CostResponse]:
        """Evaluate multiple inputs for cost."""
        raise NotImplementedError("Batch evaluation not yet supported")

    def explain(
        self,
        *,
        model_name: str | None = None,
        model_type: str | None = None,
        model_provider: str | None = None,
        number_of_queries: int | None = None,
        total_prompt_tokens: int | None = None,
        total_completion_tokens: int | None = None,
        total_tokens: int | None = None,
        instance_type: str | None = None,
        average_latency: float | None = None,
        cost_map_name: str = "sys",
        **kwargs
    ) -> dict:
        """Get detailed explanation of the cost evaluation."""
        # req = CostRequest(
        #     model_name=model_name,
        #     model_type=model_type,
        #     model_provider=model_provider,
        #     number_of_queries=number_of_queries,
        #     total_prompt_tokens=total_prompt_tokens,
        #     total_completion_tokens=total_completion_tokens,
        #     total_tokens=total_tokens,
        #     instance_type=instance_type,
        #     average_latency=average_latency
        # )
        raise NotImplementedError("Explanation not yet supported") 