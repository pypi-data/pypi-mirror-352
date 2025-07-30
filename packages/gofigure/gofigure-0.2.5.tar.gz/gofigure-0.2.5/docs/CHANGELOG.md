# GOFIGURE - CHANGELOG

## [0.2.5] - June 2nd, 2025
### Added
- **Autovivification system**: Configurable auto-creation of nested structures
- **Flexible null access**: Choose between raising exceptions, returning None, or creating empty objects
- **Namespace mangling support**: Graceful degradation when all method names are taken
- **Nested autosave propagation**: Modifications to deeply nested objects trigger root saves
- **Comprehensive test suite**: 101 tests covering all functionality and edge cases

### Enhanced
- **Intelligent nested merging**: Override data merges with existing nested structures instead of replacing
- **Root reference system**: Nested objects maintain reference to root for autosave functionality
- **Improved error handling**: Better exception messages and type safety
- **Memory efficiency**: Nested objects share root references without duplication

### Technical
- Added `autovivify`, `nullaccess`, and `manglenamespace` parameters
- Implemented proper nested object lifecycle management
- Enhanced `_dataload()` with intelligent merging logic
- Added warnings for namespace conflicts when `manglenamespace=True`
- Improved method binding and decorator application

## [0.2.0] - June 2nd, 2025
### Added
- Core `Gofig` class with dual access patterns (dict-like and attribute-like)
- Support for JSON and YAML file formats with automatic detection
- File persistence with `save()` and `reload()` functionality
- Autosave capability for automatic persistence on changes
- Intelligent namespace conflict resolution for method names
- Operator overloads (`>>` for save, `<<` for reload) as fallback options
- Nested configuration support with automatic `Gofig` wrapping
- Factory methods `FromJSON()` and `FromYAML()` for easy instantiation
- Comprehensive type hints and custom exception handling
- Standalone `save()` and `reload()` functions for conflict-free access

### Technical
- Implemented `FileFormat` enum for extensible format support
- Added `@savecheck` decorator for automatic persistence triggers
- Custom exceptions: `UnsupportedFormat`, `FormatMismatch`, `NamespaceConflict`
- Load hierarchy: file → data → overrides for flexible initialization

## [0.1.0] - June 2nd, 2025
### Added
- Project initialized
- Basic directory structure established
