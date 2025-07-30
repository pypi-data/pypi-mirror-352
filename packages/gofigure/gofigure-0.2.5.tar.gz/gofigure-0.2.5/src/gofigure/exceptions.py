# ~/gofigure/src/gofigure/exceptions.py
"""
Custom exceptions for the Gofig configuration system.
"""
from __future__ import annotations
import typing as t

class GofigError(Exception):
    """Base exception for all Gofig-related errors."""
    pass

class UnsupportedFormat(GofigError):
    """Raised when attempting to use an unsupported file format."""
    def __init__(
        self,
        fmtorext: str,
        supported: t.Optional[list] = None
    ) -> None:
        msg = f"Unsupported format: '{fmtorext}'."
        if supported:
            msg += f"Supported: {', '.join(supported)}"
        super().__init__(msg)
        self.fmt = fmtorext
        self.supported = (supported or [])

class FormatMismatch(GofigError):
    """Raised when file content doesn't match the expected format."""
    def __init__(
        self,
        expected: str,
        filepath: t.Optional[str] = None
    ) -> None:
        prefix = f"File '{filepath}' content" if filepath else "Content"
        msg = f"{prefix} doesn't match expected format: {expected}"
        super().__init__(msg)
        self.expected = expected
        self.filepath = filepath

class NamespaceConflict(GofigError):
    """Raised when all preferred method names are taken by user configuration keys."""
    def __init__(
        self,
        methodtype: str,
        attempted: list
    ) -> None:
        msg = f"Cannot assign {methodtype} method -- all preferred names taken: {', '.join(attempted)}"
        super().__init__(msg)
        self.methodtype = methodtype
        self.attempted = attempted
