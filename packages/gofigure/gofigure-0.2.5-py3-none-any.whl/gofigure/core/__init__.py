# ~/gofigure/src/gofigure/core/__init__.py
"""
Core configuration system components.

This module contains the main Gofig class and supporting utilities for
dynamic configuration management with dual access patterns (dict-like
and attribute-like) and file persistence.
"""
from .base import (
    FileFormat, Gofig,
    savecheck, save, reload
)

__all__ = [
    'FileFormat',
    'Gofig',
    'savecheck',
    'save',
    'reload'
]
