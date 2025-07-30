# ~/gofigure/tests/test_integration.py
"""
Integration tests for end-to-end Gofig workflows.
"""
import json
import yaml
import pytest
from pathlib import Path

from gofigure import Gofig, save, reload, FileFormat
from gofigure.exceptions import NamespaceConflict


class TestExampleWorkflows:
    """Test the exact examples from the README/requirements."""

    def test_basic_usage_example(self, temp_dir):
        """Test the basic usage example from README."""
        # Create test data matching the example
        test_data = {
            "name": "blah",
            "category": "blah blah",
            "tags": ["tag1", "tag2"],
            "nested": {
                "option": "value"
            }
        }

        # Create JSON file
        json_path = temp_dir / "config.json"
        with open(json_path, 'w') as f:
            json.dump(test_data, f)

        # Test the exact example workflow
        conf = Gofig.FromJSON(path=json_path)

        assert conf.name == "blah"
        assert conf['category'] == "blah blah"

        conf.nested.option = "othervalue"
        assert conf.nested['option'] == "othervalue"

        conf.reload()
        assert conf.get("nested", {}).get("option") == "value"

        conf.nested.option = "othervalue"
        conf.save()

        # Verify persistence
        conf.reload()
        assert conf.nested.option == "othervalue"

    def test_autosave_example(self, temp_dir):
        """Test the autosave example from README."""
        # Create YAML file with same data
        test_data = {
            "name": "blah",
            "category": "blah blah",
            "tags": ["tag1", "tag2"],
            "nested": {
                "option": "value"
            }
        }

        yaml_path = temp_dir / "settings.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(test_data, f)

        # Test autosave workflow
        config = Gofig.FromYAML(path=yaml_path, autosave=True, autovivify=False, nullaccess=AttributeError)

        # Test error cases
        with pytest.raises(AttributeError):
            _ = config.newvalue

        with pytest.raises(KeyError):
            _ = config['newvalue']

        assert config.get('newvalue') is None

        # Test autosave
        print(f"Before: _autosave={config._autosave}, _filepath={config._filepath}")
        print(f"_namespaced={config._namespaced}")
        config['newvalue'] = "bleh"
        print("After setting newvalue")

        # Check if it was saved
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        print(f"File contents: {data}")

        # Should be immediately saved
        config.reload()
        assert config.newvalue == "bleh"

    def test_namespace_conflict_example(self, temp_dir):
        """Test namespace conflict resolution example."""
        # Create config with conflicting keys
        conflicted_data = {
            "save": "important_user_data",
            "reload": "user_reload_data",
            "name": "test_config"
        }

        json_path = temp_dir / "conflicted.json"
        with open(json_path, 'w') as f:
            json.dump(conflicted_data, f)

        config = Gofig.FromJSON(json_path)

        # User data should be accessible
        assert config.save == "important_user_data"
        assert config['reload'] == "user_reload_data"

        # But save method should still work under different name
        config.test_key = "test_value"

        # Find which save method was assigned
        save_method_name = config._namespaced['save']
        save_method = getattr(config, save_method_name)
        save_method()  # Should work

        # Standalone functions should always work
        config.another_key = "another_value"
        save(config)

        config.another_key = "modified"
        reload(config)
        assert config.another_key == "another_value"


class TestComplexWorkflows:
    """Test complex real-world workflows."""

    def test_application_config_workflow(self, temp_dir):
        """Test realistic application configuration workflow."""
        config_path = temp_dir / "app_config.json"

        # Initialize app config
        app_config = Gofig(filepath=config_path, autosave=True)

        # Set up database configuration
        app_config.database.host = "localhost"
        app_config.database.port = 5432
        app_config.database.name = "myapp"
        app_config.database.credentials.username = "admin"
        app_config.database.credentials.password = "secret"

        # Set up API configuration
        app_config.api.base_url = "https://api.example.com"
        app_config.api.version = "v1"
        app_config.api.endpoints.users = "/users"
        app_config.api.endpoints.posts = "/posts"
        app_config.api.rate_limit = 1000

        # Set up logging
        app_config.logging.level = "INFO"
        app_config.logging.file = "/var/log/myapp.log"
        app_config.logging.rotate = True

        # Environment-specific settings
        app_config.environment = "development"
        app_config.debug = True

        # Verify structure and autosave
        assert config_path.exists()

        # Create new instance to verify persistence
        app_config2 = Gofig.FromJSON(config_path)

        assert app_config2.database.host == "localhost"
        assert app_config2.api.endpoints.users == "/users"
        assert app_config2.logging.level == "INFO"
        assert app_config2.debug is True

        # Test modification and reload
        app_config2.database.port = 3306
        save(app_config2)

        reload(app_config)
        assert app_config.database.port == 3306

    def test_multi_environment_config(self, temp_dir):
        """Test managing multiple environment configurations."""
        # Base configuration
        base_config = {
            "app_name": "MyApp",
            "version": "1.0.0",
            "database": {
                "driver": "postgresql",
                "pool_size": 10
            },
            "cache": {
                "type": "redis"
            }
        }

        # Development overrides
        dev_overrides = {
            "debug": True,
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp_dev"
            },
            "cache": {
                "host": "localhost",
                "port": 6379
            }
        }

        # Production overrides
        prod_overrides = {
            "debug": False,
            "database": {
                "host": "prod-db.example.com",
                "port": 5432,
                "name": "myapp_prod"
            },
            "cache": {
                "host": "prod-cache.example.com",
                "port": 6379
            }
        }

        # Test development config
        dev_config = Gofig(
            data=base_config,
            filepath=temp_dir / "dev_config.yaml",
            **dev_overrides
        )

        assert dev_config.app_name == "MyApp"  # From base
        assert dev_config.debug is True  # From dev overrides
        assert dev_config.database.host == "localhost"  # From dev overrides
        assert dev_config.database.driver == "postgresql"  # From base

        # Test production config
        prod_config = Gofig(
            data=base_config,
            filepath=temp_dir / "prod_config.yaml",
            **prod_overrides
        )

        assert prod_config.app_name == "MyApp"  # From base
        assert prod_config.debug is False  # From prod overrides
        assert prod_config.database.host == "prod-db.example.com"  # From prod overrides

        # Save both configs
        save(dev_config)
        save(prod_config)

        # Verify they're different files with different content
        assert (temp_dir / "dev_config.yaml").exists()
        assert (temp_dir / "prod_config.yaml").exists()

        with open(temp_dir / "dev_config.yaml") as f:
            dev_data = yaml.safe_load(f)
        with open(temp_dir / "prod_config.yaml") as f:
            prod_data = yaml.safe_load(f)

        assert dev_data['debug'] is True
        assert prod_data['debug'] is False
        assert dev_data['database']['host'] == "localhost"
        assert prod_data['database']['host'] == "prod-db.example.com"

    def test_config_migration_workflow(self, temp_dir):
        """Test configuration migration between formats."""
        # Start with JSON config
        json_config = {
            "version": "1.0",
            "settings": {
                "theme": "dark",
                "language": "en"
            },
            "features": {
                "notifications": True,
                "analytics": False
            }
        }

        json_path = temp_dir / "config.json"
        with open(json_path, 'w') as f:
            json.dump(json_config, f)

        # Load from JSON
        config = Gofig.FromJSON(json_path)

        # Add some new settings
        config.settings.font_size = 14
        config.settings.auto_save = True
        config.features.dark_mode = True

        # Migrate to YAML
        yaml_path = temp_dir / "config.yaml"
        config._filepath = yaml_path
        config._fileformat = FileFormat.FromPath(yaml_path)

        save(config)

        # Load from YAML to verify migration
        yaml_config = Gofig.FromYAML(yaml_path)

        assert yaml_config.version == "1.0"
        assert yaml_config.settings.theme == "dark"
        assert yaml_config.settings.font_size == 14
        assert yaml_config.features.dark_mode is True

    def test_operator_overload_workflow(self, temp_dir):
        """Test operator overload workflow for extreme namespace conflicts."""
        # Create config where ALL preferred names are taken
        extreme_conflict = {
            "save": "data1", "Save": "data2", "SAVE": "data3",
            "persist": "data4", "write": "data5",
            "reload": "data6", "Reload": "data7", "RELOAD": "data8",
            "refresh": "data9", "reread": "data10"
        }

        json_path = temp_dir / "extreme.json"
        with open(json_path, 'w') as f:
            json.dump(extreme_conflict, f)

        # This should still work, but might need operator overloads
        config = Gofig.FromJSON(json_path, manglenamespace=True)

        # Verify all conflict data is accessible
        assert config.save == "data1"
        assert config.Save == "data2"
        assert config.reload == "data6"

        # Test operator overloads as fallback
        config.test_operator = "operator_test"

        # Save using >> operator
        result = config >> None
        assert result is config

        # Modify and reload using << operator
        config.test_operator = "modified"
        result = config << None
        assert result is config
        assert config.test_operator == "operator_test"  # Should be restored


class TestErrorRecovery:
    """Test error recovery and edge cases."""

    def test_corrupt_file_recovery(self, temp_dir):
        """Test handling of corrupt configuration files."""
        json_path = temp_dir / "corrupt.json"

        # Create valid config first
        config = Gofig({"valid": "data"}, filepath=json_path)
        save(config)

        # Corrupt the file
        with open(json_path, 'w') as f:
            f.write("invalid json content {")

        # Should raise appropriate error on reload
        with pytest.raises(json.JSONDecodeError):
            reload(config)

    def test_permission_error_handling(self, temp_dir):
        """Test handling of permission errors."""
        config = Gofig({"test": "data"})

        # Try to save to non-existent directory with no permissions
        config._filepath = Path("/root/no_permission/config.json")
        config._fileformat = "json"

        # Should raise PermissionError or FileNotFoundError
        with pytest.raises((PermissionError, FileNotFoundError, OSError)):
            save(config)

    def test_concurrent_modification(self, temp_dir):
        """Test handling of concurrent file modifications."""
        json_path = temp_dir / "concurrent.json"

        # Create two instances of same config
        config1 = Gofig({"shared": "data"}, filepath=json_path)
        save(config1)

        config2 = Gofig.FromJSON(json_path)

        # Modify both
        config1.value1 = "from_config1"
        config2.value2 = "from_config2"

        # Save both (last one wins)
        save(config1)
        save(config2)

        # Reload config1 to see config2's changes
        reload(config1)
        assert config1.value2 == "from_config2"
        assert 'value1' not in config1  # Lost config1's changes


class TestPerformance:
    """Test performance characteristics."""

    def test_large_config_performance(self, temp_dir):
        """Test performance with large configuration data."""
        # Create large nested structure
        large_config = Gofig(filepath=temp_dir / "large.json")

        # Add many nested levels and keys
        for i in range(100):
            section = f"section_{i}"
            large_config[section] = {}
            for j in range(50):
                key = f"key_{j}"
                large_config[section][key] = f"value_{i}_{j}"

        # Test save performance
        save(large_config)

        # Test reload performance
        reload(large_config)

        # Verify data integrity
        assert large_config.section_50.key_25 == "value_50_25"
        assert len(large_config) == 100

    def test_deep_nesting_performance(self, temp_dir):
        """Test performance with deeply nested structures."""
        config = Gofig(filepath=temp_dir / "deep.yaml")

        # Create deep nesting (50 levels)
        current = config
        for i in range(50):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]

        current.deep_value = "found_it"

        # Test save/reload with deep nesting
        save(config)
        reload(config)

        # Verify deep access still works
        deep_ref = config
        for i in range(50):
            deep_ref = deep_ref[f"level_{i}"]

        assert deep_ref.deep_value == "found_it"
