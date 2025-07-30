# ~/gofigure/src/gofigure/__init__.py
"""
Gofigure - A dynamic configuration system with flexible access patterns.

Gofigure provides a powerful yet simple way to manage configuration data with
both dictionary-like and attribute-like access patterns. It supports automatic
file persistence, nested configurations, and intelligent namespace conflict
resolution.

Basic Usage:
   >>> from gofigure import Gofig
   >>> config = Gofig.FromJSON('config.json')
   >>> config.database.host = 'localhost'
   >>> config['api']['key'] = 'secret'
   >>> config.save()

Features:
   - Dual access patterns: config.key and config['key']
   - Automatic nested structure handling
   - File persistence (JSON, YAML) with autosave
   - Namespace conflict resolution for method names
   - Type-safe with full typing support
"""

__version__ = "0.2.5"
__author__ = "Joel Yisrael"
__email__ = "schizoprada@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/schizoprada/gofigure"

# Version info tuple for programmatic access
VERSION = tuple(map(int, __version__.split('.')))

from .exceptions import (
    GofigError,
    UnsupportedFormat,
    FormatMismatch,
    NamespaceConflict
)
from .core import (
    FileFormat,
    Gofig,
    savecheck,
    save,
    reload
)

__all__ = [
    'GofigError',
    'UnsupportedFormat',
    'FormatMismatch',
    'NamespaceConflict',
    'FileFormat',
    'Gofig',
    'savecheck',
    'save',
    'reload'
]
