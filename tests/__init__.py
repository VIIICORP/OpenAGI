"""Test suite initialization for OpenAGI."""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def setup_test_environment(temp_data_dir, monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("DATA_DIR", str(temp_data_dir))
    monkeypatch.setenv("AI_MODEL_CACHE_DIR", str(temp_data_dir / "models"))
    monkeypatch.setenv("ENVIRONMENT", "testing")