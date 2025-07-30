# ~/gofigure/tests/test_io.py
"""
Tests for file I/O and persistence functionality.
"""
import json
import yaml
import pytest
from pathlib import Path

from gofigure import Gofig, save, reload
from gofigure.core.base import FileFormat
from gofigure.exceptions import UnsupportedFormat


class TestFactoryMethods:
    """Test factory methods for creating Gofig instances from files."""

    def test_from_json(self, temp_json_file, sample_data):
        """Test FromJSON factory method."""
        config = Gofig.FromJSON(temp_json_file)

        assert config.name == sample_data['name']
        assert config.nested.option == sample_data['nested']['option']
        assert config._filepath == temp_json_file
        assert config._fileformat == FileFormat.JSON

    def test_from_yaml(self, temp_yaml_file, sample_data):
        """Test FromYAML factory method."""
        config = Gofig.FromYAML(temp_yaml_file)

        assert config.name == sample_data['name']
        assert config.nested.option == sample_data['nested']['option']
        assert config._filepath == temp_yaml_file
        assert config._fileformat == FileFormat.YAML

    def test_from_json_with_autosave(self, temp_json_file):
        """Test FromJSON with autosave enabled."""
        config = Gofig.FromJSON(temp_json_file, autosave=True)
        assert config._autosave is True

    def test_from_yaml_with_autosave(self, temp_yaml_file):
        """Test FromYAML with autosave enabled."""
        config = Gofig.FromYAML(temp_yaml_file, autosave=True)
        assert config._autosave is True

    def test_from_nonexistent_file(self, temp_dir):
        """Test loading from nonexistent file raises FileNotFoundError."""
        nonexistent = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            Gofig.FromJSON(nonexistent)

        with pytest.raises(FileNotFoundError):
            Gofig.FromYAML(nonexistent)


class TestSaveMethod:
    """Test save functionality."""

    def test_save_json(self, basic_gofig, temp_dir):
        """Test saving to JSON file."""
        json_path = temp_dir / "test_save.json"
        basic_gofig._filepath = json_path
        basic_gofig._fileformat = FileFormat.JSON

        # Modify data
        basic_gofig.new_key = "new_value"
        basic_gofig.nested.new_nested = "nested_value"

        # Save
        save(basic_gofig)

        # Verify file exists and content
        assert json_path.exists()
        with open(json_path) as f:
            data = json.load(f)

        assert data['new_key'] == "new_value"
        assert data['nested']['new_nested'] == "nested_value"

    def test_save_yaml(self, basic_gofig, temp_dir):
        """Test saving to YAML file."""
        yaml_path = temp_dir / "test_save.yaml"
        basic_gofig._filepath = yaml_path
        basic_gofig._fileformat = FileFormat.YAML

        # Modify data
        basic_gofig.yaml_key = "yaml_value"

        # Save
        save(basic_gofig)

        # Verify file exists and content
        assert yaml_path.exists()
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        assert data['yaml_key'] == "yaml_value"

    def test_save_creates_directory(self, basic_gofig, temp_dir):
        """Test that save creates parent directories."""
        nested_path = temp_dir / "nested" / "dir" / "config.json"
        basic_gofig._filepath = nested_path
        basic_gofig._fileformat = FileFormat.JSON

        # Directory shouldn't exist yet
        assert not nested_path.parent.exists()

        # Save should create it
        save(basic_gofig)

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_save_without_filepath(self, basic_gofig):
        """Test save without filepath raises error."""
        basic_gofig._filepath = None

        with pytest.raises(ValueError, match="No filepath configured"):
            save(basic_gofig)

    def test_save_unsupported_format(self, basic_gofig, temp_dir):
        """Test save with unsupported format raises error."""
        basic_gofig._filepath = temp_dir / "test.txt"
        basic_gofig._fileformat = "unsupported"

        with pytest.raises(UnsupportedFormat):
            save(basic_gofig)


class TestReloadMethod:
    """Test reload functionality."""

    def test_reload_json(self, temp_json_file, sample_data):
        """Test reloading from JSON file."""
        config = Gofig.FromJSON(temp_json_file)

        # Modify in memory
        config.name = "modified"
        config.new_key = "new"
        assert config.name == "modified"

        # Reload should restore original
        reload(config)
        assert config.name == sample_data['name']
        assert 'new_key' not in config

    def test_reload_yaml(self, temp_yaml_file, sample_data):
        """Test reloading from YAML file."""
        config = Gofig.FromYAML(temp_yaml_file)

        # Modify in memory
        config.category = "modified"

        # Reload should restore original
        reload(config)
        assert config.category == sample_data['category']

    def test_reload_without_filepath(self, basic_gofig):
        """Test reload without filepath raises error."""
        basic_gofig._filepath = None

        with pytest.raises(ValueError, match="No filepath configured"):
            reload(basic_gofig)

    def test_reload_nonexistent_file(self, basic_gofig, temp_dir):
        """Test reload with nonexistent file raises error."""
        basic_gofig._filepath = temp_dir / "nonexistent.json"

        with pytest.raises(ValueError, match="file doesn't exist"):
            reload(basic_gofig)

    def test_reload_resets_dynamic_methods(self, temp_json_file):
        """Test that reload resets dynamic method assignments."""
        # Create config with conflicting data
        conflicted_data = {"save": "user_data", "reload": "user_data"}

        # Save conflicted data to file
        with open(temp_json_file, 'w') as f:
            json.dump(conflicted_data, f)

        config = Gofig.FromJSON(temp_json_file)

        # Should have dynamic methods assigned
        assert hasattr(config, '_namespaced')

        # Reload should maintain method assignments
        original_namespaced = config._namespaced.copy()
        reload(config)

        assert config._namespaced == original_namespaced


class TestAutosave:
    """Test autosave functionality."""

    def test_autosave_on_setitem(self, autosave_json_file, sample_data):
        """Test autosave triggers on __setitem__."""
        config = Gofig.FromJSON(autosave_json_file, autosave=True)

        # Modify via dict access
        config['autosave_test'] = "triggered"

        # Should be immediately saved to file
        with open(autosave_json_file) as f:
            data = json.load(f)

        assert data['autosave_test'] == "triggered"

    def test_autosave_on_setattr(self, autosave_yaml_file, sample_data):
        """Test autosave triggers on __setattr__."""
        config = Gofig.FromYAML(autosave_yaml_file, autosave=True)

        # Modify via attribute access
        config.autosave_attr = "triggered"

        # Should be immediately saved to file
        with open(autosave_yaml_file) as f:
            data = yaml.safe_load(f)

        assert data['autosave_attr'] == "triggered"

    def test_autosave_nested_modification(self, autosave_json_file, sample_data):
        """Test autosave triggers on nested modifications."""
        config = Gofig.FromJSON(autosave_json_file, autosave=True)

        # Debug prints
        #print(f"config._autosave: {config._autosave}")
        #print(f"config._filepath: {config._filepath}")
        #print(f"config.nested type: {type(config.nested)}")
        #print(f"config.nested._root: {getattr(config.nested, '_root', 'NOT SET')}")
        #print(f"config.nested._shouldautosave(): {config.nested._shouldautosave()}")


        # Modify nested value
        config.nested.autosave_nested = "nested_triggered"

        #print("After setting nested value...")

        # Should be saved to file
        with open(autosave_json_file) as f:
            data = json.load(f)

        #print(f"File contents: {data}")


        assert data['nested']['autosave_nested'] == "nested_triggered"

    def test_no_autosave_when_disabled(self, temp_json_file, sample_data):
        """Test autosave doesn't trigger when disabled."""
        config = Gofig.FromJSON(temp_json_file, autosave=False)

        # Modify data
        config.no_autosave = "not_saved"

        # Should NOT be in file yet
        with open(temp_json_file) as f:
            data = json.load(f)

        assert 'no_autosave' not in data

        # Manual save should work
        save(config)

        with open(temp_json_file) as f:
            data = json.load(f)

        assert data['no_autosave'] == "not_saved"


class TestRoundTrip:
    """Test round-trip save/reload cycles."""

    def test_json_round_trip(self, temp_dir, sample_data):
        """Test JSON save/reload preserves data."""
        json_path = temp_dir / "roundtrip.json"

        # Create and save
        config = Gofig(sample_data, filepath=json_path)
        config.round_trip = "test"
        save(config)

        # Load fresh instance
        config2 = Gofig.FromJSON(json_path)

        assert config2.round_trip == "test"
        assert config2.name == sample_data['name']
        assert config2.nested.option == sample_data['nested']['option']

    def test_yaml_round_trip(self, temp_dir, sample_data):
        """Test YAML save/reload preserves data."""
        yaml_path = temp_dir / "roundtrip.yaml"

        # Create and save
        config = Gofig(sample_data, filepath=yaml_path)
        config.yaml_round_trip = "test"
        save(config)

        # Load fresh instance
        config2 = Gofig.FromYAML(yaml_path)

        assert config2.yaml_round_trip == "test"
        assert config2.name == sample_data['name']
        assert config2.nested.option == sample_data['nested']['option']

    def test_nested_round_trip(self, temp_dir):
        """Test deeply nested data round trip."""
        json_path = temp_dir / "nested.json"

        # Create deeply nested structure
        config = Gofig(filepath=json_path)
        config.level1.level2.level3.deep_value = "deep"
        config.level1.level2.other_value = "other"
        save(config)

        # Reload and verify
        config2 = Gofig.FromJSON(json_path)
        assert config2.level1.level2.level3.deep_value == "deep"
        assert config2.level1.level2.other_value == "other"

        # All should be Gofig instances
        assert isinstance(config2.level1, Gofig)
        assert isinstance(config2.level1.level2, Gofig)
        assert isinstance(config2.level1.level2.level3, Gofig)


class TestFileFormatDetection:
    """Test automatic file format detection."""

    def test_json_format_detection(self, temp_dir, sample_data):
        """Test JSON format is detected from file extension."""
        json_path = temp_dir / "test.json"
        config = Gofig(sample_data, filepath=json_path)

        assert config._fileformat == FileFormat.JSON

    def test_yaml_format_detection(self, temp_dir, sample_data):
        """Test YAML format is detected from file extensions."""
        yaml_path = temp_dir / "test.yaml"
        config = Gofig(sample_data, filepath=yaml_path)
        assert config._fileformat == FileFormat.YAML

        yml_path = temp_dir / "test.yml"
        config2 = Gofig(sample_data, filepath=yml_path)
        assert config2._fileformat == FileFormat.YAML

    def test_unsupported_format_detection(self, temp_dir, sample_data):
        """Test unsupported format raises error during init."""
        txt_path = temp_dir / "test.txt"

        with pytest.raises(UnsupportedFormat):
            Gofig(sample_data, filepath=txt_path)
