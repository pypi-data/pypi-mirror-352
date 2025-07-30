Usage
=================

This section provides comprehensive documentation on how to use the Trustwise SDK, including basic setup, configuration, and detailed examples for evaluating different metrics.

Basic Setup
-----------

Here's how to set up and configure the Trustwise SDK:

.. code-block:: python

    import os
    from trustwise.sdk import TrustwiseSDK
    from trustwise.sdk.config import TrustwiseConfig

    # Configure using environment variables
    os.environ["TW_API_KEY"] = "your-api-key"
    os.environ["TW_BASE_URL"] = "https://api.trustwise.ai"
    config = TrustwiseConfig()

    # Or configure directly
    # config = TrustwiseConfig(
    #     api_key="your-api-key",
    #     base_url="https://api.trustwise.ai"
    # )

    # Initialize the SDK
    trustwise = TrustwiseSDK(config)

Evaluating Metrics
------------------

Below are example requests and responses for evaluating different metrics using the SDK. Each metric exposes an `evaluate()` endpoint.

Faithfulness Metric
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Example request
    result = trustwise.metrics.faithfulness.evaluate(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        context=[
            {"node_id": "1", "node_score": 1.0, "node_text": "Paris is the capital of France."}
        ]
    )

    # Example response object
    # {
    #     "score": 95.5,
    #     "facts": [
    #         {
    #             "statement": "Paris is the capital of France",
    #             "label": "VERIFIED",
    #             "prob": 0.98,
    #             "sentence_span": [0, 28]
    #         }
    #     ]
    # }

Cost Metric
~~~~~~~~~~~

.. code-block:: python

    # Example request
    cost_result = trustwise.metrics.cost.evaluate(
        model_name="gpt-3.5-turbo",
        model_type="LLM",
        model_provider="OpenAI",
        number_of_queries=5,
        total_prompt_tokens=950,
        total_completion_tokens=50,
        instance_type="a1.large",
        average_latency=653
    )

    # Example response object
    # {
    #     "cost_estimate_per_run": 0.0025,
    #     "total_project_cost_estimate": 0.0125
    # }

Carbon Metric
~~~~~~~~~~~~~

.. code-block:: python

    # Example request
    carbon_result = trustwise.metrics.carbon.evaluate(
        processor_name="RTX 3080",
        provider_name="aws",
        provider_region="us-east-1",
        instance_type="a1.metal",
        average_latency=653
    )

    # Example response object
    # {
    #     "carbon_emitted": 0.00015,
    #     "sci_per_api_call": 0.00003,
    #     "sci_per_10k_calls": 0.3
    # }

Guardrails
~~~~~~~~~~

.. code-block:: python

    # Create a multi-metric guardrail
    guardrail = trustwise.guardrails(
        thresholds={
            "faithfulness": 0.8,
            "answer_relevancy": 0.7,
            "clarity": 0.7
        },
        block_on_failure=True
    )

    # Evaluate with multiple metrics
    evaluation = guardrail.evaluate(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        context=context
    )

    # Example evaluation object
    # {
    #     "passed": True,
    #     "blocked": False,
    #     "results": {
    #         "faithfulness": {"passed": True, "result": {"score": 1.0}},
    #         "answer_relevancy": {"passed": True, "result": {"score": 0.95}},
    #         "clarity": {"passed": True, "result": {"score": 0.9}}
    #     }
    # }
