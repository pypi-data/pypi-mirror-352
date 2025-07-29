# Promptplex

A Python library for mastering AI prompts with versioning, templating, and testing. Navigate the complexity of prompt engineering with ease.

## Features

- **Complex Template Management**: Handle sophisticated prompt architectures
- **Version Control**: Track evolution of your prompt systems
- **Validation Engine**: Ensure template integrity and correctness
- **Testing Matrix**: Comprehensive testing across multiple scenarios
- **Persistent Storage**: Organize and preserve your prompt library
- **Enterprise Patterns**: Production-ready prompt templates

## Installation

```bash
pip install promptplex
```

## Quick Start

```python
from promptplex import PromptManager, PromptTemplate

# Initialize Promptplex
manager = PromptManager()

# Build a complex template
template = PromptTemplate(
    name="advanced_code_review",
    template="Review this {language} code:\n\n{code}\n\nAnalyze: {focus_areas}",
    variables=["language", "code", "focus_areas"],
    description="Advanced code review system"
)

# Integrate into your workflow
manager.add_template(template)

# Execute with precision
review_prompt = template.render(
    language="Python",
    code="def hello(): print('world')",
    focus_areas="performance, security, maintainability"
)

print(review_prompt)
```

## Core Concepts

### PromptTemplate

A PromptTemplate represents a reusable prompt with placeholders for variables:

```python
template = PromptTemplate(
    name="summarize",
    template="Summarize this text in {length} sentences:\n\n{text}",
    variables=["text", "length"],
    version="1.0",
    description="Text summarization template",
    tags=["summarization", "text"]
)
```

### PromptManager

The PromptManager handles storage, versioning, and organization of templates:

```python
manager = PromptManager(storage_path=".prompts")

# Add templates
manager.add_template(template)

# Get templates
template = manager.get_template("summarize")

# List all templates
print(manager.list_templates())

# Export/import templates
manager.export_templates("my_prompts.yaml")
manager.import_templates("shared_prompts.yaml")
```

### PromptTester

Test your templates with multiple inputs and compare variations:

```python
from promptplex import PromptTester

tester = PromptTester(manager)

test_cases = [
    {"text": "Long article text...", "length": "3"},
    {"text": "Another article...", "length": "1"}
]

results = tester.test_template("summarize", test_cases)

# Compare different templates
comparison = tester.compare_templates(
    ["summarize_v1", "summarize_v2"], 
    test_cases
)
```

## Built-in Templates

Promptplex includes enterprise-grade templates:

```python
from promptplex import setup_builtin_templates

setup_builtin_templates(manager)

# Available templates:
# - code_review: For reviewing code
# - summarize: For text summarization  
# - chat_assistant: For chat/assistant prompts
```

## Advanced Usage

### Template Validation

Templates are automatically validated when created:

```python
# This will raise an error if template syntax is invalid
template.validate()

# Get a hash for change detection
hash_value = template.get_hash()
```

### Custom Evaluators

Add custom evaluation logic to your tests:

```python
def evaluate_summary(output, inputs):
    # Custom logic to evaluate summary quality
    return {
        "length_appropriate": len(output.split()) < 100,
        "contains_key_points": "important" in output.lower()
    }

results = tester.test_template("summarize", test_cases, evaluator=evaluate_summary)
```

### Working with Files

Templates are automatically saved to disk and loaded when needed:

```python
# Templates are saved in .promptplex/ directory by default
manager = PromptManager()  # Uses .promptplex/
manager = PromptManager("./my_prompts")  # Custom directory
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=promptplex
```

### Code Formatting

```bash
# Format code
black promptplex tests

# Check types
mypy promptplex
```

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## License

MIT License - see LICENSE file for details.