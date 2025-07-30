Welcome to Trustwise SDK's documentation!
=========================================

Trustwise SDK is a powerful tool for evaluating AI-generated content with Trustwise's unified Metrics API.

Quickstart
----------

1. **Install the SDK:**

   .. code-block:: bash

      pip install trustwise

2. **Set up and run your first evaluation:**

   .. code-block:: python

      import os
      from trustwise.sdk import TrustwiseSDK
      from trustwise.sdk.config import TrustwiseConfig

      # Initialize the SDK
      config = TrustwiseConfig(api_key=os.environ["TW_API_KEY"])
      trustwise = TrustwiseSDK(config)

      # Evaluate faithfulness
      result = trustwise.metrics.faithfulness.evaluate(
          query="What is the capital of France?",
          response="The capital of France is Paris.",
          context=[{"node_id": "doc:idx:1", "node_score": 0.95, "node_text": "Paris is the capital of France."}]
      )
      print(f"Faithfulness score: {result['score']}")

Documentation Overview
----------------------

This documentation is organized to help you quickly find what you need:

- **Usage:** Get started with basic setup, configuration, and comprehensive examples (:doc:`usage`)
- **Metrics:** Detailed documentation for all available evaluation metrics (see :ref:`metrics`)
- **API Reference:** Full technical documentation for all SDK features and metrics (:doc:`api`)
- **API Versioning:** Use explicit or default API versions for flexibility (:doc:`versioning`)
- **Changelog:** Track documentation changes and feature additions (:doc:`changelog`)

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   usage
   metrics
   api
   versioning
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 