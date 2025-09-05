# Contributing to OpenAGI

We welcome contributions to OpenAGI! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## 🔧 Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/OpenAGI.git
cd OpenAGI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

## 📝 Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Include type hints where appropriate
- Keep functions focused and small

## 🧪 Testing

- Write tests for new features
- Ensure all existing tests pass
- Aim for high test coverage
- Use pytest for testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=openagi tests/
```

## 📚 Adding New Features

When adding new AI features to OpenAGI:

1. Create a new class inheriting from `AIFeature`
2. Implement the `execute` method
3. Add appropriate tags and metadata
4. Include comprehensive documentation
5. Add tests for the feature
6. Update the feature loading function

Example:
```python
class MyNewFeature(AIFeature):
    def __init__(self):
        super().__init__("my_new_feature", "category", "Description")
        self.tags = ["tag1", "tag2"]
    
    def execute(self, *args, **kwargs):
        # Implementation here
        return result
```

## 🐛 Bug Reports

When reporting bugs, please include:

- Python version and OS
- OpenAGI version
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any error messages or stack traces

## 💡 Feature Requests

We welcome feature requests! Please:

- Check if the feature already exists
- Describe the use case
- Explain the expected behavior
- Consider if it fits OpenAGI's scope

## 📖 Documentation

- Update documentation for new features
- Use clear, concise language
- Include code examples
- Update the README if necessary

## 🚦 Pull Request Process

1. Ensure your code follows the style guidelines
2. Update tests and documentation
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Submit your pull request with a clear description

## 📄 License

By contributing to OpenAGI, you agree that your contributions will be licensed under the Apache License 2.0.

## 🙏 Thank You

Thank you for contributing to OpenAGI! Your contributions help make AI more accessible to everyone.