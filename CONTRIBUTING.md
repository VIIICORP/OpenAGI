# Contributing to OpenAGI

We welcome contributions to the OpenAGI platform! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/VIIICORP/OpenAGI.git
   cd OpenAGI
   ```

2. **Set up development environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements-dev.txt
   pip install -e .
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Set up configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

5. **Initialize database**:
   ```bash
   openagi db init
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openagi --cov-report=html

# Run specific test categories
pytest tests/test_basic.py -v
pytest -k "test_platform" -v

# Run self-tests
openagi test run --suite quick
```

### Writing Tests

- Write comprehensive tests for new features
- Follow existing test patterns and naming conventions
- Include both unit tests and integration tests
- Test edge cases and error conditions
- Ensure tests are deterministic and can run in parallel

Example test structure:
```python
import pytest
from openagi import OpenAGI

class TestNewFeature:
    @pytest.fixture
    def agi_platform(self):
        return OpenAGI(auto_start=False)
    
    @pytest.mark.asyncio
    async def test_new_functionality(self, agi_platform):
        # Test implementation
        pass
```

## 🎯 Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use `black` for code formatting
- Use `flake8` for linting
- Use `mypy` for type checking
- Maximum line length: 100 characters

```bash
# Format code
black openagi/

# Check linting
flake8 openagi/

# Type checking
mypy openagi/
```

### Documentation

- Write clear docstrings for all public functions and classes
- Use Google-style docstrings
- Include type hints for all function signatures
- Update README.md for significant changes
- Add examples for new features

Example docstring:
```python
async def process_data(
    self, 
    data: Dict[str, Any], 
    options: Optional[ProcessingOptions] = None
) -> ProcessingResult:
    """
    Process input data through the AI pipeline.
    
    Args:
        data: Input data to process
        options: Optional processing configuration
        
    Returns:
        ProcessingResult with outputs and metadata
        
    Raises:
        ValueError: If data format is invalid
        ProcessingError: If processing fails
        
    Examples:
        >>> result = await platform.process_data({"text": "hello"})
        >>> print(result.outputs)
    """
```

### Commit Messages

Use conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(testing): add performance benchmarking suite
fix(models): resolve memory leak in model loading
docs(readme): update installation instructions
test(api): add integration tests for REST endpoints
```

## 🏗 Architecture Guidelines

### Adding New Models

1. Inherit from `BaseModel`
2. Implement all abstract methods
3. Add comprehensive tests
4. Update model registry
5. Add documentation and examples

```python
from openagi.models.base import BaseModel

class YourCustomModel(BaseModel):
    async def load(self) -> bool:
        # Implementation
        pass
    
    async def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass
```

### Adding New Test Categories

1. Add category to `TestCategory` enum
2. Implement test generator in `TestGenerator`
3. Update test distribution configuration
4. Add category-specific metrics and assertions

### Adding New API Endpoints

1. Create endpoint in `openagi/api/`
2. Add request/response models
3. Implement proper error handling
4. Add authentication if required
5. Write API tests
6. Update API documentation

## 🔄 Development Workflow

### Branch Strategy

- `main`: Stable release branch
- `develop`: Development integration branch
- `feature/*`: Feature development branches
- `hotfix/*`: Critical bug fixes

### Pull Request Process

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **PR Requirements**:
   - Clear description of changes
   - Reference related issues
   - All tests pass
   - Code coverage maintained
   - Documentation updated
   - Pre-commit hooks pass

### Review Process

- All PRs require at least one review
- Automated checks must pass
- Manual testing for significant changes
- Documentation review for public APIs

## 🐛 Issue Reporting

### Bug Reports

Include:
- OpenAGI version
- Python version
- Operating system
- Minimal reproduction case
- Expected vs actual behavior
- Relevant logs/error messages

### Feature Requests

Include:
- Clear use case description
- Proposed implementation approach
- Impact on existing functionality
- Examples of usage

## 📋 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release branch
- [ ] Tag release
- [ ] Deploy to package registry
- [ ] Update Docker images
- [ ] Announce release

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Invited to contributor discussions
- Eligible for contributor badges

## 📞 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and community support
- **Discord**: Real-time community chat
- **Email**: maintainers@openagi.dev for private matters

## 🙏 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

---

Thank you for contributing to OpenAGI! 🚀