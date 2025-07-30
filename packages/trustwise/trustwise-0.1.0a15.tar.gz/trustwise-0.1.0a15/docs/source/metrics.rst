.. _metrics:

Metrics
=======
The SDK provides access to all metrics through the unified ``metrics`` namespace. Each metric provides an ``evaluate()`` function. Example usage:

.. code-block:: python

    result = trustwise.metrics.faithfulness.evaluate(query="...", response="...", context=[...])
    clarity = trustwise.metrics.clarity.evaluate(query="...", response="...")
    cost = trustwise.metrics.cost.evaluate(model_name="...", model_type="LLM", ...)

Refer to the API reference for details on each metric's parameters.

.. note::
   Custom types such as ``Context`` are defined in the :ref:`types section <types>`. Please refer to :mod:`trustwise.sdk.types` for details on these types.

Faithfulness
~~~~~~~~~~~~
.. function:: metrics.faithfulness.evaluate(query: :class:`str`, response: :class:`str`, context: :class:`~trustwise.sdk.types.Context`) -> FaithfulnessResponse

   Evaluate the faithfulness of a response against its context.

   Parameters:
   - query (str): The input query
   - response (str): The response to evaluate
   - context (:class:`~trustwise.sdk.types.Context`): Context information (list of :class:`~trustwise.sdk.types.ContextNode`)

   Returns:
   - FaithfulnessResponse: Example response:

     .. code-block:: json

        {
            "score": 95.5,
            "facts": [
                {
                    "statement": "Paris is the capital of France",
                    "label": "VERIFIED",
                    "prob": 0.98,
                    "sentence_span": [0, 28]
                }
            ]
        }

Answer Relevancy
~~~~~~~~~~~~~~~~
.. function:: metrics.answer_relevancy.evaluate(query: :class:`str`, response: :class:`str`, context: :class:`~trustwise.sdk.types.Context`) -> AnswerRelevancyResponse

   Evaluate the relevancy of a response to the query.

   Parameters:
   - query (str): The input query
   - response (str): The response to evaluate
   - context (:class:`~trustwise.sdk.types.Context`): Context information (see :ref:`types`)

   Returns:
   - AnswerRelevancyResponse: Example response:

     .. code-block:: json

        {
            "score": 92.0,
            "generated_question": "What is the capital city of France?"
        }

Context Relevancy
~~~~~~~~~~~~~~~~~
.. function:: metrics.context_relevancy.evaluate(query: :class:`str`, context: :class:`~trustwise.sdk.types.Context`, response: :class:`str`) -> ContextRelevancyResponse

   Evaluate the relevancy of the context to the query.

   Parameters:
   - query (str): The input query
   - context (:class:`~trustwise.sdk.types.Context`): Context information (see :ref:`types`)
   - response (str): The response to evaluate

   Returns:
   - ContextRelevancyResponse: Example response:

     .. code-block:: json

        {
            "score": 88.5,
            "topics": ["geography", "capitals", "France"],
            "scores": [0.92, 0.85, 0.88]
        }

Summarization
~~~~~~~~~~~~~
.. function:: metrics.summarization.evaluate(query: :class:`str`, response: :class:`str`, context: :class:`~trustwise.sdk.types.Context`) -> SummarizationResponse

   Evaluate the quality of a summary.

   Parameters:
   - query (str): The input query
   - response (str): The response to evaluate
   - context (:class:`~trustwise.sdk.types.Context`): Context information (see :ref:`types`)

   Returns:
   - SummarizationResponse: Example response:

     .. code-block:: json

        {
            "score": 90.0
        }

PII
~~~
.. function:: metrics.pii.evaluate(text: :class:`str`, allowlist: :class:`list`\[:class:`str`\], blocklist: :class:`list`\[:class:`str`\]) -> PIIResponse

   Detect personally identifiable information in text.

   Parameters:
   - text (str): The text to analyze
   - allowlist (List[str]): List of allowed PII patterns
   - blocklist (List[str]): List of blocked PII patterns

   Returns:
   - PIIResponse: Example response:

     .. code-block:: json

        {
            "identified_pii": [
                {
                    "interval": [0, 5],
                    "string": "Hello",
                    "category": "blocklist"
                },
                {
                    "interval": [94, 111],
                    "string": "www.wikipedia.org",
                    "category": "organization"
                }
            ]
        }

Prompt Injection
~~~~~~~~~~~~~~~~
.. function:: metrics.prompt_injection.evaluate(query: :class:`str`, response: :class:`str`, context: :class:`list`\[:class:`~trustwise.sdk.types.ContextNode`\]) -> PromptInjectionResponse

   Detect potential prompt injection attempts.

   Parameters:
   - query (str): The input query
   - response (str): The response to evaluate
   - context (:class:`list`\[:class:`~trustwise.sdk.types.ContextNode`\]): Context information (list of context nodes)

   Returns:
   - PromptInjectionResponse: Example response:

     .. code-block:: json

        {
            "score": 98.0
        }

Clarity
~~~~~~~
.. function:: metrics.clarity.evaluate(query: :class:`str`, response: :class:`str`) -> ClarityResponse

   Evaluate the clarity of a response.

   Parameters:
   - query (str): The input query
   - response (str): The response to evaluate

   Returns:
   - ClarityResponse: Example response:

     .. code-block:: json

        {
            "score": 92.5
        }

Helpfulness
~~~~~~~~~~~
.. function:: metrics.helpfulness.evaluate(query: :class:`str`, response: :class:`str`) -> HelpfulnessResponse

   Evaluate the helpfulness of a response.

   Parameters:
   - query (str): The input query
   - response (str): The response to evaluate

   Returns:
   - HelpfulnessResponse: Example response:

     .. code-block:: json

        {
            "score": 88.0
        }

Formality
~~~~~~~~~
.. function:: metrics.formality.evaluate(response: :class:`str`) -> FormalityResponse

   Evaluate the formality level of a response.

   Parameters:
   - response (str): The response to evaluate

   Returns:
   - FormalityResponse: Example response:

     .. code-block:: json

        {
            "score": 75.0,
            "sentences": [
                "The capital of France is Paris."
            ],
            "scores": [0.75]
        }

Simplicity
~~~~~~~~~~
.. function:: metrics.simplicity.evaluate(response: :class:`str`) -> SimplicityResponse

   Evaluate the simplicity of a response.

   Parameters:
   - response (str): The response to evaluate

   Returns:
   - SimplicityResponse: Example response:

     .. code-block:: json

        {
            "score": 82.0
        }

Sensitivity
~~~~~~~~~~~
.. function:: metrics.sensitivity.evaluate(response: :class:`str`, topics: :class:`list`\[:class:`str`\], query: :class:`Optional`\[:class:`str`\]) -> SensitivityResponse

   Evaluate the sensitivity of a response regarding specific topics.

   Parameters:
   - response (str): The response to evaluate
   - topics (List[str]): List of topics to evaluate sensitivity for
   - query (Optional[str]): Optional input query

   Returns:
   - SensitivityResponse: Example response:

     .. code-block:: json

        {
            "scores": {
                "politics": 0.70,
                "religion": 0.60
            }
        }

Toxicity
~~~~~~~~
.. function:: metrics.toxicity.evaluate(query: :class:`Optional`\[:class:`str`\], response: :class:`Optional`\[:class:`str`\], user_id: :class:`Optional`\[:class:`str`\] = None) -> ToxicityResponse

   Evaluate the toxicity of a response.

   Parameters:
   - query (Optional[str]): Optional input query
   - response (Optional[str]): Optional response
   - user_id (Optional[str]): Optional user identifier

   Returns:
   - ToxicityResponse: Example response:

     .. code-block:: json

        {
            "labels": ["hate", "harassment"],
            "scores": [0.10, 0.05]
        }

Tone
~~~~
.. function:: metrics.tone.evaluate(response: :class:`str`, query: :class:`Optional`\[:class:`str`\] = None) -> ToneResponse

   Evaluate the tone of a response.

   Parameters:
   - response (str): The response to evaluate
   - query (Optional[str]): Optional input query

   Returns:
   - ToneResponse: Example response:

     .. code-block:: json

        {
            "labels": ["PROFESSIONAL", "NEUTRAL"],
            "scores": [0.85, 0.75]
        }

Cost
~~~~
.. function:: metrics.cost.evaluate(model_name: :class:`str`, model_type: :class:`str`, model_provider: :class:`str`, number_of_queries: :class:`int`, total_prompt_tokens: :class:`Optional`\[:class:`int`\] = None, total_completion_tokens: :class:`Optional`\[:class:`int`\] = None, total_tokens: :class:`Optional`\[:class:`int`\] = None, instance_type: :class:`Optional`\[:class:`str`\] = None, average_latency: :class:`Optional`\[:class:`float`\] = None) -> CostResponse

   Evaluates the cost of API usage based on token counts, model information, and infrastructure details.

   Parameters:
   - model_name (str): Name of the model
   - model_type (str): Type of model (LLM or Reranker)
   - model_provider (str): Provider of the model
   - number_of_queries (int): Number of queries to evaluate
   - total_prompt_tokens (Optional[int]): Total prompt tokens
   - total_completion_tokens (Optional[int]): Total completion tokens
   - total_tokens (Optional[int]): Total tokens (for Together Reranker)
   - instance_type (Optional[str]): Instance type (for Hugging Face)
   - average_latency (Optional[float]): Average latency in milliseconds

   Returns:
   - CostResponse: Example response:

     .. code-block:: json

        {
            "cost_estimate_per_run": 0.0025,
            "total_project_cost_estimate": 0.0125
        }

Carbon
~~~~~~
.. function:: metrics.carbon.evaluate(processor_name: :class:`str`, provider_name: :class:`str`, provider_region: :class:`str`, instance_type: :class:`str`, average_latency: :class:`int`) -> CarbonResponse

   Evaluates the carbon emissions based on hardware specifications and infrastructure details.

   Parameters:
   - processor_name (str): Name of the processor
   - provider_name (str): Name of the cloud provider
   - provider_region (str): Region of the cloud provider
   - instance_type (str): Type of instance
   - average_latency (int): Average latency in milliseconds

   Returns:
   - CarbonResponse: Example response:

     .. code-block:: json

        {
            "carbon_emitted": 0.00015,
            "sci_per_api_call": 0.00003,
            "sci_per_10k_calls": 0.3
        }

.. note::
   For more details on SDK usage and advanced features, see the :doc:`api` reference. 