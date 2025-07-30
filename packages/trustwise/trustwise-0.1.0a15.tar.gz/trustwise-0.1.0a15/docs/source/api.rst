API Reference
=============

This section provides detailed technical documentation for the Trustwise SDK. For conceptual information and best practices, see the individual metric sections.

SDK
---

.. automodule:: trustwise.sdk
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

.. automodule:: trustwise.sdk.config
   :members:
   :undoc-members:
   :show-inheritance:

Types
-----

.. automodule:: trustwise.sdk.types
   :members:
   :undoc-members:
   :show-inheritance:

Guardrails
----------

.. automodule:: trustwise.sdk.guardrails
   :members:
   :undoc-members:
   :show-inheritance:

The SDK provides a guardrail system to enforce safety and alignment metrics thresholds. The guardrail system can be used to:

- Set thresholds for multiple metrics
- Block responses that fail metric checks
- Execute callbacks when metrics are evaluated
- Check for PII content with custom allowlists and blocklists

Example usage:

.. code-block:: python

    trustwise = TrustwiseSDK(config)
    guardrail = trustwise.guardrails(
        thresholds={
            "faithfulness": 0.8,
            "answer_relevancy": 0.7,
            "clarity": 0.7
        },
        block_on_failure=True
    )
    evaluation = guardrail.evaluate(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        context=context
    )
    # Pythonic access
    print(evaluation.passed)
    print(evaluation.results['faithfulness']['result'].score)
    # Serialization
    print(evaluation.to_dict())
    print(evaluation.to_json(indent=2))

The guardrail system returns a :class:`GuardrailResponse`