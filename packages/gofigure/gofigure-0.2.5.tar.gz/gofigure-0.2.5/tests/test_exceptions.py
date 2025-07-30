# ~/gofigure/tests/test_exceptions.py
"""
Tests for custom Gofig exceptions.
"""
import pytest
from gofigure.exceptions import (
    GofigError,
    UnsupportedFormat,
    FormatMismatch,
    NamespaceConflict
)


class TestGofigError:
    """Test base GofigError exception."""

    def test_is_exception(self):
        """Test that GofigError is a proper exception."""
        assert issubclass(GofigError, Exception)

    def test_can_be_raised(self):
        """Test that GofigError can be raised and caught."""
        with pytest.raises(GofigError):
            raise GofigError("Test error")

    def test_inheritance_chain(self):
        """Test that all custom exceptions inherit from GofigError."""
        assert issubclass(UnsupportedFormat, GofigError)
        assert issubclass(FormatMismatch, GofigError)
        assert issubclass(NamespaceConflict, GofigError)


class TestUnsupportedFormat:
    """Test UnsupportedFormat exception."""

    def test_basic_creation(self):
        """Test basic exception creation."""
        exc = UnsupportedFormat("txt")
        assert str(exc) == "Unsupported format: 'txt'."
        assert exc.fmt == "txt"
        assert exc.supported == []

    def test_with_supported_formats(self):
        """Test exception with supported formats list."""
        supported = ["json", "yaml"]
        exc = UnsupportedFormat("xml", supported)

        assert "Unsupported format: 'xml'." in str(exc)
        assert "Supported: json, yaml" in str(exc)
        assert exc.fmt == "xml"
        assert exc.supported == supported

    def test_empty_supported_list(self):
        """Test with empty supported list."""
        exc = UnsupportedFormat("txt", [])
        assert str(exc) == "Unsupported format: 'txt'."
        assert exc.supported == []

    def test_can_be_caught(self):
        """Test that exception can be caught."""
        with pytest.raises(UnsupportedFormat) as exc_info:
            raise UnsupportedFormat("bad_format", ["good_format"])

        assert exc_info.value.fmt == "bad_format"
        assert "good_format" in exc_info.value.supported

    def test_inheritance(self):
        """Test inheritance from GofigError."""
        exc = UnsupportedFormat("test")
        assert isinstance(exc, GofigError)
        assert isinstance(exc, Exception)


class TestFormatMismatch:
    """Test FormatMismatch exception."""

    def test_basic_creation(self):
        """Test basic exception creation."""
        exc = FormatMismatch("json")
        assert str(exc) == "Content doesn't match expected format: json"
        assert exc.expected == "json"
        assert exc.filepath is None

    def test_with_filepath(self):
        """Test exception with filepath."""
        exc = FormatMismatch("yaml", "/path/to/file.txt")
        expected_msg = "File '/path/to/file.txt' content doesn't match expected format: yaml"
        assert str(exc) == expected_msg
        assert exc.expected == "yaml"
        assert exc.filepath == "/path/to/file.txt"

    def test_without_filepath(self):
        """Test exception without filepath."""
        exc = FormatMismatch("xml")
        assert str(exc) == "Content doesn't match expected format: xml"
        assert exc.filepath is None

    def test_can_be_caught(self):
        """Test that exception can be caught."""
        with pytest.raises(FormatMismatch) as exc_info:
            raise FormatMismatch("json", "test.yaml")

        assert exc_info.value.expected == "json"
        assert exc_info.value.filepath == "test.yaml"

    def test_inheritance(self):
        """Test inheritance from GofigError."""
        exc = FormatMismatch("test")
        assert isinstance(exc, GofigError)
        assert isinstance(exc, Exception)


class TestNamespaceConflict:
    """Test NamespaceConflict exception."""

    def test_basic_creation(self):
        """Test basic exception creation."""
        attempted = ["save", "Save", "SAVE"]
        exc = NamespaceConflict("save", attempted)

        expected_msg = "Cannot assign save method -- all preferred names taken: save, Save, SAVE"
        assert str(exc) == expected_msg
        assert exc.methodtype == "save"
        assert exc.attempted == attempted

    def test_reload_method_conflict(self):
        """Test with reload method conflict."""
        attempted = ["reload", "Reload", "refresh"]
        exc = NamespaceConflict("reload", attempted)

        assert "reload method" in str(exc)
        assert "reload, Reload, refresh" in str(exc)
        assert exc.methodtype == "reload"
        assert exc.attempted == attempted

    def test_single_attempted_name(self):
        """Test with single attempted name."""
        exc = NamespaceConflict("test", ["test_name"])
        assert "test_name" in str(exc)
        assert exc.attempted == ["test_name"]

    def test_empty_attempted_list(self):
        """Test with empty attempted list."""
        exc = NamespaceConflict("save", [])
        assert str(exc) == "Cannot assign save method -- all preferred names taken: "
        assert exc.attempted == []

    def test_can_be_caught(self):
        """Test that exception can be caught."""
        attempted = ["name1", "name2"]
        with pytest.raises(NamespaceConflict) as exc_info:
            raise NamespaceConflict("test_method", attempted)

        assert exc_info.value.methodtype == "test_method"
        assert exc_info.value.attempted == attempted

    def test_inheritance(self):
        """Test inheritance from GofigError."""
        exc = NamespaceConflict("test", [])
        assert isinstance(exc, GofigError)
        assert isinstance(exc, Exception)


class TestExceptionChaining:
    """Test exception chaining and context."""

    def test_raise_from_other_exception(self):
        """Test raising custom exceptions from other exceptions."""
        try:
            # Simulate a scenario where we catch one exception and raise our own
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise UnsupportedFormat("bad_format") from e
        except UnsupportedFormat as exc:
            assert exc.fmt == "bad_format"
            assert isinstance(exc.__cause__, ValueError)

    def test_exception_in_context(self):
        """Test exceptions work in various contexts."""
        exceptions_to_test = [
            UnsupportedFormat("test"),
            FormatMismatch("json", "file.txt"),
            NamespaceConflict("save", ["save", "Save"])
        ]

        for exc in exceptions_to_test:
            # Test that they can be raised and caught
            with pytest.raises(GofigError):
                raise exc

            # Test that they have proper string representation
            assert str(exc)

            # Test that they are instances of the right classes
            assert isinstance(exc, GofigError)
            assert isinstance(exc, Exception)


class TestExceptionAttributes:
    """Test that exception attributes are properly set and accessible."""

    def test_unsupported_format_attributes(self):
        """Test UnsupportedFormat attribute access."""
        exc = UnsupportedFormat("txt", ["json", "yaml"])

        # Test direct attribute access
        assert exc.fmt == "txt"
        assert exc.supported == ["json", "yaml"]

        # Test that attributes are settable (though not recommended)
        exc.fmt = "xml"
        assert exc.fmt == "xml"

    def test_format_mismatch_attributes(self):
        """Test FormatMismatch attribute access."""
        exc = FormatMismatch("json", "/path/file.txt")

        assert exc.expected == "json"
        assert exc.filepath == "/path/file.txt"

        # Test None filepath
        exc2 = FormatMismatch("yaml")
        assert exc2.filepath is None

    def test_namespace_conflict_attributes(self):
        """Test NamespaceConflict attribute access."""
        attempted = ["save", "Save", "SAVE", "persist"]
        exc = NamespaceConflict("save", attempted)

        assert exc.methodtype == "save"
        assert exc.attempted == attempted
        #assert exc.attempted is not attempted  # Should be a copy, not reference
