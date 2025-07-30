API Versioning
==============

The Trustwise SDK provides flexible version management through both explicit version paths and default version usage for backward compatibility.

Version Management
------------------

Available Versions
~~~~~~~~~~~~~~~~~~

Get the available API versions:

.. code-block:: python

    from trustwise.sdk import TrustwiseSDK, TrustwiseConfig

    config = TrustwiseConfig(api_key="your-api-key")
    trustwise = TrustwiseSDK(config)

    # Get available versions
    versions = trustwise.get_versions()

Current Version
~~~~~~~~~~~~~~~~~~~~~

Get and set the current default version for a specific API:

.. code-block:: python

    # Get current version
    trustwise.metrics.version

Usage Patterns
--------------

The SDK supports three equivalent ways to access API versions:

Explicit Version Path
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Using explicit version path
    result = trustwise.metrics.v3.faithfulness.evaluate(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        context=[{"node_id": "doc:idx:1", "node_score": 0.95, "node_text": "Paris is the capital of France."}]
    )

Default Version
~~~~~~~~~~~~~~~

.. code-block:: python

    # Using default version: points to the latest available version
    result = trustwise.metrics.faithfulness.evaluate(
        query="What is the capital of France?",
        response="The capital of France is Paris.",
        context=[{"node_id": "doc:idx:1", "node_score": 0.95, "node_text": "Paris is the capital of France."}]
    )

Supported Versions
------------------

The following API versions are currently supported:

- **Metrics API**: v3