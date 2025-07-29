# LLM Model Cost Calculator

A Python package to calculate token costs for various LLM models based on input and output tokens.

## Installation

```bash
pip install llm_model_cost
```

## Usage

```python
from llm_model_cost import modelCost

# Calculate cost for a model
cost = modelCost(name="gpt-4", input_tokens=100, output_tokens=50)

# Get cost details
print(f"Input cost: ${cost['input_cost']:.6f}")
print(f"Output cost: ${cost['output_cost']:.6f}")
print(f"Total cost: ${cost['total_cost']:.6f}")

# Get model information
model_info = modelCost.get_model_info("gpt-4")
print(f"Max tokens: {model_info['max_tokens']}")
print(f"Provider: {model_info['litellm_provider']}")

# List all available models
models = modelCost.list_models()
```

## Features

- Calculate token costs for various LLM models
- Get model information including max tokens, costs, and provider details
- List all available models and their capabilities
- Automatic updates from the latest pricing data

## License

MIT License 