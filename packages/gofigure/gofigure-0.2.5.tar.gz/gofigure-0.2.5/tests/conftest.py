# ~/gofigure/tests/conftest.py
"""
Test configuration and fixtures for gofigure tests.
"""
import json
import yaml
import tempfile
import pytest
from pathlib import Path
from typing import Dict, Any

from gofigure import Gofig


@pytest.fixture
def sample_data() -> Dict[str, Any]:
    """Sample configuration data for testing."""
    return {
        "name": "test_config",
        "category": "testing",
        "tags": ["test", "sample"],
        "nested": {
            "option": "value",
            "number": 42,
            "enabled": True
        },
        "list_data": [1, 2, 3],
        "empty_dict": {}
    }


@pytest.fixture
def temp_json_file(sample_data):
    """Create a temporary JSON file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        json_path = Path(f.name)

    yield json_path

    # Cleanup
    if json_path.exists():
        json_path.unlink()


@pytest.fixture
def temp_yaml_file(sample_data):
    """Create a temporary YAML file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_data, f)
        yaml_path = Path(f.name)

    yield yaml_path

    # Cleanup
    if yaml_path.exists():
        yaml_path.unlink()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def basic_gofig(sample_data):
    """Create a basic Gofig instance with sample data."""
    return Gofig(sample_data)


@pytest.fixture
def conflicted_data():
    """Data that conflicts with Gofig method names."""
    return {
        "save": "user_save_data",
        "reload": "user_reload_data",
        "get": "user_get_data",
        "nested": {
            "save": "nested_save_data"
        }
    }


@pytest.fixture
def conflicted_gofig(conflicted_data):
    """Gofig instance with namespace conflicts."""
    return Gofig(conflicted_data)


@pytest.fixture
def autosave_json_file(sample_data, temp_dir):
    """JSON file for autosave testing."""
    json_path = temp_dir / "autosave_test.json"
    with open(json_path, 'w') as f:
        json.dump(sample_data, f)
    return json_path


@pytest.fixture
def autosave_yaml_file(sample_data, temp_dir):
    """YAML file for autosave testing."""
    yaml_path = temp_dir / "autosave_test.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(sample_data, f)
    return yaml_path
