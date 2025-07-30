Changelog
=========

All notable changes to the Trustwise SDK will be documented in this file.

v1.0.0 (2024-03-21)
-------------------

Features
~~~~~~~~

Core Evaluation
^^^^^^^^^^^^^^^

- Introduced comprehensive evaluation system for AI-generated content
- Added support for context-based evaluation with node scoring
- Implemented query-response evaluation framework

Metrics
-------

- Added support for context-based faithfulness, answer relevancy, and other metrics
- Implemented query-response alignment scoring
- Added cost and carbon evaluation for model runs

Guardrails System
^^^^^^^^^^^^^^^^^

- Added multi-metric guardrail system with configurable thresholds
- Implemented block-on-failure functionality
- Added support for comprehensive evaluation result aggregation
- Introduced flexible threshold configuration per metric

Version Management
^^^^^^^^^^^^^^^^^^

- Added explicit version support for all API endpoints
- Implemented default version fallback system
- Added version switching capabilities
- Introduced version-aware evaluation methods

Configuration
^^^^^^^^^^^^^

- Added environment variable based configuration
- Implemented direct configuration through TrustwiseConfig
- Added support for API key and base URL configuration
- Introduced flexible configuration options for all features 