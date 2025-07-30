# GOFIGURE

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-101%20passed-brightgreen.svg)](#)
[![Zero Dependencies*](https://img.shields.io/badge/dependencies-minimal-success.svg)](#requirements)

*Only PyYAML for YAML support

A dynamic configuration system with flexible access patterns for Python. Zero external dependencies except PyYAML.

## ✨ Features

- **🔄 Dual Access Patterns**: Use both `config.key` and `config['key']` interchangeably
- **💾 File Persistence**: Automatic loading/saving with JSON and YAML support
- **🌳 Smart Nesting**: Automatic handling of nested dictionaries with autovivification
- **🛡️ Namespace Protection**: Intelligent method naming when your data conflicts
- **⚡ Autosave**: Optional automatic persistence on configuration changes
- **🔒 Type Safe**: Full typing support with comprehensive error handling
- **🎯 Zero Config**: Works out of the box with sensible defaults

## 🚀 Quick Start

```python
from gofigure import Gofig

# Load from file
config = Gofig.FromJSON('config.json')

# Dual access patterns
config.database.host = 'localhost'        # Attribute access
config['database']['port'] = 5432         # Dict access

# Automatic nesting (autovivification)
config.api.endpoints.users = '/api/v1/users'
print(config.api.endpoints.users)  # /api/v1/users

# Save changes
config.save()

# Autosave mode - changes persist immediately
config = Gofig.FromYAML('settings.yaml', autosave=True)
config.debug = True  # Automatically saved!
```

## 📦 Installation

```bash
pip install gofigure
```

## 🔧 Advanced Usage

### Autovivification Control

```python
# Default: auto-create nested structures
config = Gofig(autovivify=True)
config.new.nested.key = "value"  # Creates nested structure automatically

# Strict mode: only access existing keys
config = Gofig(autovivify=False, nullaccess=AttributeError)
config.nonexistent  # Raises AttributeError

# Return None for missing keys
config = Gofig(autovivify=False, nullaccess=None)
print(config.missing)  # None
```

### Namespace Conflict Resolution

```python
# Automatic resolution
config = Gofig({'save': 'important_data'})
config.Save()  # Uses 'Save' instead of 'save'

# Standalone functions (always available)
from gofigure import save, reload
save(config)
reload(config)

# Extreme conflicts - use operators
config = Gofig({
    'save': 'data', 'Save': 'data', 'persist': 'data'
}, manglenamespace=True)
config >> ...  # Save via operator
config << ...  # Reload via operator
```

### Flexible Initialization

```python
# Hierarchy: file → data → overrides
config = Gofig(
    data={'defaults': True},
    filepath='config.json',
    autosave=True,
    environment='production',  # Override
    debug=False               # Override
)
```

### Error Handling

```python
from gofigure import UnsupportedFormat, NamespaceConflict

try:
    config = Gofig.FromJSON('config.xml')  # Wrong format
except UnsupportedFormat as e:
    print(f"Format not supported: {e.fmt}")
    print(f"Supported formats: {e.supported}")
```

## 📋 Supported Formats

| Format | Extensions | Status |
|--------|------------|--------|
| **JSON** | `.json` | ✅ Full support |
| **YAML** | `.yaml`, `.yml` | ✅ Full support |
| **TOML** | `.toml` | 🚧 Coming soon |

## 🔬 Technical Features

- **Smart Merging**: Nested configurations merge intelligently
- **Memory Efficient**: Shared root references for nested objects
- **Type Hints**: Full typing support with generics
- **Comprehensive Tests**: 101 tests covering edge cases
- **No Magic**: Clear, predictable behavior

## 📝 Requirements

- **Python 3.9+**
- **PyYAML 6.0+** (for YAML support)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">
<sub>Built with ❤️ and zero unnecessary dependencies</sub>
</div>
