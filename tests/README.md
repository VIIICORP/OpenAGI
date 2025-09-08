# OpenAGI Tests

This directory contains the test suite for OpenAGI.

## Test Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for the complete platform

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_core.py

# Run with coverage
pytest --cov=openagi tests/

# Run tests with verbose output
pytest -v tests/
```

## Test Requirements

Install test dependencies:

```bash
pip install -e .[dev]
```

## Writing Tests

Follow these guidelines when writing tests:

1. Use descriptive test names
2. Test both success and failure cases
3. Use appropriate fixtures for setup
4. Keep tests isolated and independent
5. Add integration tests for complex workflows