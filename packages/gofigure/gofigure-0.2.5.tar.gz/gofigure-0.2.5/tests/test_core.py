# ~/gofigure/tests/test_core.py
"""
Tests for core Gofig functionality.
"""
import pytest
from gofigure import Gofig, save, reload
from gofigure.exceptions import NamespaceConflict


class TestGofigBasics:
    """Test basic Gofig functionality."""

    def test_init_empty(self):
        """Test creating empty Gofig instance."""
        config = Gofig()
        assert len(config) == 0
        assert isinstance(config, dict)
        assert isinstance(config, Gofig)

    def test_init_with_data(self, sample_data):
        """Test creating Gofig with initial data."""
        config = Gofig(sample_data)
        assert config['name'] == "test_config"
        assert config.name == "test_config"
        assert len(config) == len(sample_data)

    def test_nested_gofig_creation(self, sample_data):
        """Test that nested dicts become Gofig instances."""
        config = Gofig(sample_data)
        assert isinstance(config.nested, Gofig)
        assert config.nested.option == "value"
        assert config.nested['number'] == 42


class TestDualAccess:
    """Test dual access patterns (dict-like and attribute-like)."""

    def test_dict_access_get(self, basic_gofig):
        """Test dictionary-style getting."""
        assert basic_gofig['name'] == "test_config"
        assert basic_gofig['nested']['option'] == "value"

    def test_dict_access_set(self, basic_gofig):
        """Test dictionary-style setting."""
        basic_gofig['new_key'] = "new_value"
        assert basic_gofig['new_key'] == "new_value"
        assert basic_gofig.new_key == "new_value"

    def test_attr_access_get(self, basic_gofig):
        """Test attribute-style getting."""
        assert basic_gofig.name == "test_config"
        assert basic_gofig.nested.option == "value"

    def test_attr_access_set(self, basic_gofig):
        """Test attribute-style setting."""
        basic_gofig.new_attr = "attr_value"
        assert basic_gofig.new_attr == "attr_value"
        assert basic_gofig['new_attr'] == "attr_value"

    def test_nested_dict_auto_wrap(self, basic_gofig):
        """Test that assigned dicts become Gofig instances."""
        new_dict = {"level2": {"level3": "deep"}}
        basic_gofig.deep_nested = new_dict

        assert isinstance(basic_gofig.deep_nested, Gofig)
        assert isinstance(basic_gofig.deep_nested.level2, Gofig)
        assert basic_gofig.deep_nested.level2.level3 == "deep"


class TestErrorHandling:
    """Test error handling for missing keys/attributes."""

    def test_missing_key_error(self, basic_gofig):
        """Test KeyError for missing dict keys."""
        with pytest.raises(KeyError):
            _ = basic_gofig['nonexistent']

    def test_missing_attr_error(self, basic_gofig):
        """Test AttributeError for missing attributes."""
        basic_gofig._autovivify = False
        basic_gofig._nullaccess = AttributeError
        with pytest.raises(AttributeError):
            _ = basic_gofig.nonexistent

    def test_get_method_default(self, basic_gofig):
        """Test get() method with defaults."""
        assert basic_gofig.get('nonexistent') is None
        assert basic_gofig.get('nonexistent', 'default') == 'default'
        assert basic_gofig.get('name') == "test_config"


class TestNamespaceConflicts:
    """Test namespace conflict resolution."""

    def test_conflicted_data_access(self, conflicted_gofig):
        """Test accessing data that conflicts with method names."""
        assert conflicted_gofig.save == "user_save_data"
        assert conflicted_gofig['reload'] == "user_reload_data"
        assert conflicted_gofig.nested.save == "nested_save_data"

    def test_save_method_still_available(self, conflicted_gofig):
        """Test that save method is still available under different name."""
        # Should have some save method available (Save, SAVE, persist, etc.)
        found_save_method = False
        for name in Gofig._SAVENAMES:
            if hasattr(conflicted_gofig, name) and callable(getattr(conflicted_gofig, name)):
                found_save_method = True
                break
        assert found_save_method

    def test_reload_method_still_available(self, conflicted_gofig):
        """Test that reload method is still available under different name."""
        found_reload_method = False
        for name in Gofig._RELOADNAMES:
            if hasattr(conflicted_gofig, name) and callable(getattr(conflicted_gofig, name)):
                found_reload_method = True
                break
        assert found_reload_method

    def test_standalone_functions_work(self, conflicted_gofig, temp_json_file):
        """Test that standalone save/reload functions work despite conflicts."""
        conflicted_gofig._filepath = temp_json_file
        conflicted_gofig._fileformat = "json"

        # These should always work regardless of namespace conflicts
        save(conflicted_gofig)
        conflicted_gofig.new_key = "test"
        reload(conflicted_gofig)

        # new_key should be gone after reload
        assert 'new_key' not in conflicted_gofig


class TestOperatorOverloads:
    """Test operator overloads for save/reload."""

    def test_rshift_save(self, basic_gofig, temp_json_file):
        """Test >> operator for saving."""
        basic_gofig._filepath = temp_json_file
        basic_gofig._fileformat = "json"

        result = basic_gofig >> None
        assert result is basic_gofig  # Should return self
        assert temp_json_file.exists()

    def test_lshift_reload(self, basic_gofig, temp_json_file):
        """Test << operator for reloading."""
        basic_gofig._filepath = temp_json_file
        basic_gofig._fileformat = "json"

        # Modify and save
        basic_gofig.test_key = "test_value"
        basic_gofig >> None

        # Modify again
        basic_gofig.test_key = "modified"

        # Reload should restore saved value
        result = basic_gofig << None
        assert result is basic_gofig
        assert basic_gofig.test_key == "test_value"


class TestInternalAttributes:
    """Test that internal attributes don't interfere with data."""

    def test_internal_attrs_not_in_dict(self, basic_gofig):
        """Test that _filepath, _autosave, etc. aren't in dict data."""
        assert '_filepath' not in basic_gofig
        assert '_autosave' not in basic_gofig
        assert '_fileformat' not in basic_gofig

    def test_internal_attrs_accessible(self, basic_gofig):
        """Test that internal attributes are still accessible."""
        assert hasattr(basic_gofig, '_filepath')
        assert hasattr(basic_gofig, '_autosave')
        assert hasattr(basic_gofig, '_fileformat')

    def test_setting_internal_attrs(self, basic_gofig):
        """Test setting internal attributes doesn't affect dict data."""
        original_len = len(basic_gofig)
        basic_gofig._test_internal = "test"
        assert len(basic_gofig) == original_len
        assert '_test_internal' not in basic_gofig


class TestDataTypes:
    """Test handling of various data types."""

    def test_list_preservation(self, basic_gofig):
        """Test that lists are preserved and not converted."""
        assert basic_gofig.list_data == [1, 2, 3]
        assert isinstance(basic_gofig.list_data, list)

    def test_primitive_types(self, basic_gofig):
        """Test primitive type preservation."""
        assert isinstance(basic_gofig.nested.number, int)
        assert isinstance(basic_gofig.nested.enabled, bool)
        assert isinstance(basic_gofig.name, str)

    def test_empty_dict_becomes_gofig(self, basic_gofig):
        """Test that even empty dicts become Gofig instances."""
        assert isinstance(basic_gofig.empty_dict, Gofig)
        assert len(basic_gofig.empty_dict) == 0
