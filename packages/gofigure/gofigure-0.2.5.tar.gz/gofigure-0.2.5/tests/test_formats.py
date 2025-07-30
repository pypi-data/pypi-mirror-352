# ~/gofigure/tests/test_formats.py
"""
Tests for FileFormat enum and format detection.
"""
import pytest
from pathlib import Path

from gofigure.core.base import FileFormat
from gofigure.exceptions import UnsupportedFormat


class TestFileFormat:
    """Test FileFormat enum functionality."""

    def test_enum_values(self):
        """Test enum string values."""
        assert str(FileFormat.JSON) == "json"
        assert str(FileFormat.YAML) == "yaml"
        assert FileFormat.JSON.value == "json"
        assert FileFormat.YAML.value == "yaml"

    def test_extensions_property(self):
        """Test extensions property for each format."""
        assert FileFormat.JSON.extensions == ['.json']
        assert FileFormat.YAML.extensions == ['.yaml', '.yml']


class TestFromExtension:
    """Test FileFormat.FromExtension method."""

    def test_json_extension(self):
        """Test JSON extension detection."""
        assert FileFormat.FromExtension('.json') == FileFormat.JSON
        assert FileFormat.FromExtension('json') == FileFormat.JSON
        assert FileFormat.FromExtension('.JSON') == FileFormat.JSON

    def test_yaml_extensions(self):
        """Test YAML extension detection."""
        assert FileFormat.FromExtension('.yaml') == FileFormat.YAML
        assert FileFormat.FromExtension('yaml') == FileFormat.YAML
        assert FileFormat.FromExtension('.yml') == FileFormat.YAML
        assert FileFormat.FromExtension('yml') == FileFormat.YAML
        assert FileFormat.FromExtension('.YAML') == FileFormat.YAML

    def test_unsupported_extension(self):
        """Test unsupported extension raises error."""
        with pytest.raises(UnsupportedFormat) as exc_info:
            FileFormat.FromExtension('.txt')

        assert 'txt' in str(exc_info.value)
        assert exc_info.value.fmt == 'txt'
        assert 'json' in exc_info.value.supported
        assert 'yaml' in exc_info.value.supported

    def test_empty_extension(self):
        """Test empty extension raises error."""
        with pytest.raises(UnsupportedFormat):
            FileFormat.FromExtension('')

    def test_no_dot_extension(self):
        """Test extension without leading dot."""
        assert FileFormat.FromExtension('json') == FileFormat.JSON
        assert FileFormat.FromExtension('yaml') == FileFormat.YAML


class TestFromPath:
    """Test FileFormat.FromPath method."""

    def test_json_path(self):
        """Test JSON path detection."""
        assert FileFormat.FromPath('config.json') == FileFormat.JSON
        assert FileFormat.FromPath('/path/to/config.json') == FileFormat.JSON
        assert FileFormat.FromPath(Path('config.json')) == FileFormat.JSON

    def test_yaml_paths(self):
        """Test YAML path detection."""
        assert FileFormat.FromPath('config.yaml') == FileFormat.YAML
        assert FileFormat.FromPath('config.yml') == FileFormat.YAML
        assert FileFormat.FromPath('/path/to/config.yaml') == FileFormat.YAML
        assert FileFormat.FromPath(Path('config.yml')) == FileFormat.YAML

    def test_unsupported_path(self):
        """Test unsupported path raises error."""
        with pytest.raises(UnsupportedFormat):
            FileFormat.FromPath('config.txt')

        with pytest.raises(UnsupportedFormat):
            FileFormat.FromPath('config.ini')

    def test_no_extension_path(self):
        """Test path without extension raises error."""
        with pytest.raises(UnsupportedFormat):
            FileFormat.FromPath('config')

        with pytest.raises(UnsupportedFormat):
            FileFormat.FromPath('/path/to/config')

    def test_complex_paths(self):
        """Test complex file paths."""
        assert FileFormat.FromPath('/home/user/configs/app.config.json') == FileFormat.JSON
        assert FileFormat.FromPath('../../relative/path/settings.yaml') == FileFormat.YAML
        assert FileFormat.FromPath('C:\\Windows\\config.yml') == FileFormat.YAML


class TestCaseInsensitivity:
    """Test case insensitive extension handling."""

    def test_mixed_case_extensions(self):
        """Test mixed case extensions work."""
        assert FileFormat.FromExtension('.JSON') == FileFormat.JSON
        assert FileFormat.FromExtension('.Json') == FileFormat.JSON
        assert FileFormat.FromExtension('.YAML') == FileFormat.YAML
        assert FileFormat.FromExtension('.Yaml') == FileFormat.YAML
        assert FileFormat.FromExtension('.YML') == FileFormat.YAML

    def test_mixed_case_paths(self):
        """Test mixed case in paths."""
        assert FileFormat.FromPath('CONFIG.JSON') == FileFormat.JSON
        assert FileFormat.FromPath('Settings.YAML') == FileFormat.YAML
        assert FileFormat.FromPath('app.YML') == FileFormat.YAML


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_multiple_dots_in_filename(self):
        """Test files with multiple dots use last extension."""
        assert FileFormat.FromPath('my.config.file.json') == FileFormat.JSON
        assert FileFormat.FromPath('backup.2023.12.01.yaml') == FileFormat.YAML

    def test_hidden_files(self):
        """Test hidden files (starting with dot)."""
        assert FileFormat.FromPath('.config.json') == FileFormat.JSON
        assert FileFormat.FromPath('.env.yaml') == FileFormat.YAML

    def test_whitespace_handling(self):
        """Test whitespace in extensions is handled."""
        # Note: This tests current behavior - whitespace might not be expected
        # but we should handle it gracefully
        with pytest.raises(UnsupportedFormat):
            FileFormat.FromExtension(' .json ')

        # But the actual extension part should work
        assert FileFormat.FromExtension('.json') == FileFormat.JSON
