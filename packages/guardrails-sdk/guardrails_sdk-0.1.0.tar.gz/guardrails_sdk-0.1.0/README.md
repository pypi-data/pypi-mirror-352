# README for Guardrails SDK

# Guardrails SDK

The Guardrails SDK is a Python library designed to facilitate interaction with the Guardrails API. It provides a simple and intuitive interface for developers to integrate safety mechanisms and quality controls into their applications powered by Large Language Models (LLMs).

## Features

- **Content Validation**: Validate user-generated content against specified guardrails to ensure safety and compliance.
- **PII Detection & Masking**: Automatically detect and mask Personally Identifiable Information (PII) in text to protect user privacy.
- **Toxicity Detection**: Identify and flag toxic language in user inputs to maintain a safe environment.

## Installation

You can install the Guardrails SDK using pip. Run the following command:

```bash
pip install guardrails-sdk
```

## Usage

Here’s a quick example of how to use the Guardrails SDK:

```python
from guardrails_sdk.client import GuardrailsClient

client = GuardrailsClient()

# Validate content
toxicity_result = client.validate_content("Your input text here")
print(toxicity_result)

# Mask PII
masked_result = client.mask_pii("Your input text with PII here")
print(masked_result)

# Detect toxicity
toxicity_detection = client.detect_toxicity("Your input text here")
print(toxicity_detection)
```

## API Reference

### GuardrailsClient

- **validate_content(content: str) -> dict**: Validates the provided content against the configured guardrails.
- **mask_pii(content: str) -> dict**: Masks any detected PII in the provided content.
- **detect_toxicity(content: str) -> dict**: Detects toxicity in the provided content and returns the results.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the terms of the Apache License 2.0. See the LICENSE file for details.