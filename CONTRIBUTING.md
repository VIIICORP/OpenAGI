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

## 👥 User Testing and Beta Program

### Becoming a Beta Tester

If you're interested in testing OpenAGI before public release:

1. **Check out our [User Testing Program](./USER_TESTING.md)**
2. **Apply through our beta testing form**: [Application Link]
3. **Join our testing community** on Discord
4. **Participate in structured testing cycles**

### User Testing Contributions

Beta testers can contribute by:

- **Bug Reports**: Report issues with detailed reproduction steps
- **Feature Feedback**: Evaluate new features and provide improvement suggestions  
- **Usability Testing**: Test user interfaces and developer experience
- **Documentation Review**: Help improve guides and tutorials
- **Performance Testing**: Validate feature performance and scalability

### Testing Guidelines

- **Be Constructive**: Provide specific, actionable feedback
- **Be Thorough**: Test edge cases and error conditions
- **Be Timely**: Report issues promptly during testing cycles
- **Be Collaborative**: Engage with other testers and the development team

### Recognition Program

Active beta testers receive:
- **Early Access**: Preview features before public release
- **Community Recognition**: Acknowledgment in release notes and community
- **Direct Impact**: Influence on product development and roadmap
- **Exclusive Resources**: Access to beta-only documentation and support

## 🙏 Thank You

Thank you for contributing to OpenAGI! Whether through code, testing, documentation, or community building, your contributions help make AI more accessible to everyone.