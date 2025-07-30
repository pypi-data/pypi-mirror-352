# 🦉 Trustwise Python SDK

[![PyPI version](https://img.shields.io/pypi/v/trustwise.svg)](https://pypi.org/project/trustwise/)

Trustwise Python SDK provides convenient access to the Trustwise Safety, Alignment and Performance metrics for any Python (3.11, 3.12) application. The library includes type definitions for all request params and response fields.

## 📦 Installation

```bash
pip install trustwise
```

## 🚀 Quick Start

Get started with Trustwise in just a few lines of code:

```python
import os
from trustwise.sdk import TrustwiseSDK
from trustwise.sdk.config import TrustwiseConfig

# Initialize the SDK
config = TrustwiseConfig(api_key=os.getenv("TW_API_KEY"))
trustwise = TrustwiseSDK(config)
```

### 🛡️ Safety Metrics

Evaluate content safety and faithfulness:

```python
# Example context
context = [{
    "node_text": "Paris is the capital of France.",
    "node_score": 0.95,
    "node_id": "doc:idx:1"
}]

# Evaluate faithfulness
result = trustwise.metrics.faithfulness.evaluate(
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    context=context
)
print(f"Faithfulness score: {result.score}")

# Evaluate PII detection
pii_result = trustwise.metrics.pii.evaluate(
    text="My email is john@example.com and my phone is 123-456-7890",
    allowlist=["john@example.com"],  # Allow specific PII patterns
    blocklist=["123-456-7890"]       # Block specific PII patterns
)
print(f"PII detection result: {pii_result}")
```

### 🎯 Alignment Metrics

Assess content quality and alignment:

```python
# Evaluate clarity
clarity_result = trustwise.metrics.clarity.evaluate(
    query="What is the capital of France?",
    response="The capital of France is Paris."
)
print(f"Clarity score: {clarity_result.score}")

# Evaluate tone
tone_result = trustwise.metrics.tone.evaluate(
    response="The capital of France is Paris."
)
print(f"Tone result: {tone_result}")
```

### 💰 Performance Metrics

Evaluate cost and carbon emissions for your AI models:

```python
# Evaluate cost for OpenAI model
cost_result = trustwise.metrics.cost.evaluate(
    model_name="gpt-3.5-turbo",
    model_type="LLM",
    model_provider="OpenAI",
    number_of_queries=5,
    total_prompt_tokens=950,
    total_completion_tokens=50
)
print(f"Cost per run: ${cost_result.cost_estimate_per_run}")
print(f"Total project cost: ${cost_result.total_project_cost_estimate}")

# Evaluate carbon emissions
carbon_result = trustwise.metrics.carbon.evaluate(
    processor_name="AMD A10-9700",
    provider_name="aws",
    provider_region="us-east-1",
    instance_type="p4d.24xlarge",
    average_latency=100
)
print(f"Carbon emissions: {carbon_result.carbon_emissions} kg CO2e")
```

### 🚧 Guardrails

Create guardrails to automatically validate responses:

```python
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

print("Guardrail Evaluation:", evaluation)
print("Guardrail Evaluation:", evaluation.to_json())
```

## 🔐 API Key Setup

Get your API Key by logging in through Github -> [link](https://trustwise.ai)

The SDK requires an API key to authenticate requests. You can provide the API key in several ways:

```python
# Method 1: Using environment variable (recommended)
config = TrustwiseConfig()  # Automatically uses TW_API_KEY from environment
trustwise = TrustwiseSDK(config)

# Method 2: Direct initialization with API key
config_direct = TrustwiseConfig(api_key=os.environ["TW_API_KEY"])
trustwise_direct = TrustwiseSDK(config_direct)

# Method 3: Custom configuration with specific base URL
config_custom = TrustwiseConfig(
    api_key=os.environ["TW_API_KEY"],
    base_url="https://api.trustwise.ai"
)
trustwise_custom = TrustwiseSDK(config_custom)
```

## 📚 API Versioning

The SDK uses the latest available API version by default. You do not need to specify a version path in your code.

```python
# Using default version (recommended)
result = trustwise.safety.faithfulness.evaluate(...)
```

## 📊 Available Metrics

- Faithfulness
- Answer Relevancy
- Context Relevancy
- Summarization
- Prompt Injection Detection
- Clarity
- Helpfulness
- Toxicity
- Tone
- Formality
- Simplicity
- Sensitivity
- Cost Estimation
- Carbon Emissions

## 📝 License

This project is licensed under the Apache License, Version 2.0 - see the LICENSE file for details.

## 🤝 Contributing

We welcome contributions! If you find a bug, have a feature request, or want to contribute code, please create an issue or submit a pull request.

### Git Hooks

This repository includes git hooks to ensure code quality. To install them:

```bash
# Make sure you're in the repository root
./scripts/install-hooks.sh
```

The hooks will run tests, linting, and documentation checks before each push to ensure code quality.