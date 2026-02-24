"""Unit tests for Evernote error handling utilities."""

import pytest

from evernote.edam.error.ttypes import (
    EDAMErrorCode,
    EDAMNotFoundException,
    EDAMSystemException,
    EDAMUserException,
)

from evernote_mcp.util.error_handler import handle_evernote_error


class TestHandleEvernoteError:
    """Test handle_evernote_error function."""

    def test_handles_edam_user_exception(self):
        """Test handling EDAMUserException."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.BAD_DATA_FORMAT,
            parameter="notebook_name",
        )

        result = handle_evernote_error(exc)
        data = result

        assert data["success"] is False
        assert "error" in data
        assert data["error_code"] == EDAMErrorCode.BAD_DATA_FORMAT
        # Note: parameter field is no longer included to avoid leaking internal details

    def test_edam_user_error_bad_data_format(self):
        """Test error message for BAD_DATA_FORMAT."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.BAD_DATA_FORMAT,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "Invalid data format" in data["error"]

    def test_edam_user_error_data_conflict(self):
        """Test error message for DATA_CONFLICT."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.DATA_CONFLICT,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "already exists" in data["error"]

    def test_edam_user_error_data_required(self):
        """Test error message for DATA_REQUIRED."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.DATA_REQUIRED,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "Required data is missing" in data["error"]

    def test_edam_user_error_enml_validation(self):
        """Test error message for ENML_VALIDATION."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.ENML_VALIDATION,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "Invalid note content format" in data["error"]

    def test_edam_user_error_limit_reached(self):
        """Test error message for LIMIT_REACHED."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.LIMIT_REACHED,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "Account limit reached" in data["error"]

    def test_edam_user_error_quota_reached(self):
        """Test error message for QUOTA_REACHED."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.QUOTA_REACHED,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "Upload quota reached" in data["error"]

    def test_edam_user_error_permission_denied(self):
        """Test error message for PERMISSION_DENIED."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.PERMISSION_DENIED,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "Permission denied" in data["error"]

    def test_edam_user_error_auth_expired(self):
        """Test error message for AUTH_EXPIRED."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.AUTH_EXPIRED,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "expired" in data["error"].lower()

    def test_edam_user_error_invalid_auth(self):
        """Test error message for INVALID_AUTH."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.INVALID_AUTH,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "Invalid authentication" in data["error"]

    def test_edam_user_error_unknown_code(self):
        """Test handling error code that returns base message."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.BAD_DATA_FORMAT,
        )
        result = handle_evernote_error(exc)
        data = result
        # BAD_DATA_FORMAT is a known code, so it returns specific message
        assert "Invalid data format" in data["error"]
    def test_edam_user_error_with_parameter(self):
        """Test that parameter is NOT included in error message (security fix)."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.BAD_DATA_FORMAT,
            parameter="title",
        )

        result = handle_evernote_error(exc)
        data = result

        # Parameter should not be exposed in error message
        assert "title" not in data["error"]
        # parameter field should not exist in response
        assert "parameter" not in data

    def test_handles_edam_system_exception(self):
        """Test handling EDAMSystemException."""
        exc = EDAMSystemException(
            errorCode=EDAMErrorCode.RATE_LIMIT_REACHED,
            message="Rate limit exceeded",
        )

        result = handle_evernote_error(exc)
        data = result

        assert data["success"] is False
        assert "System error" in data["error"]
        assert "Rate limit exceeded" in data["error"]
        assert data["error_code"] == EDAMErrorCode.RATE_LIMIT_REACHED

    def test_handles_edam_not_found_exception(self):
        """Test handling EDAMNotFoundException."""
        exc = EDAMNotFoundException(identifier="note-guid-123")

        result = handle_evernote_error(exc)
        data = result

        assert data["success"] is False
        assert "not found" in data["error"].lower()
        assert "note-guid-123" in data["error"]

    def test_handles_generic_exception(self):
        """Test handling generic Exception."""
        exc = ValueError("Something went wrong")

        result = handle_evernote_error(exc)
        data = result

        assert data["success"] is False
        assert "Something went wrong" in data["error"]
        assert "error_code" not in data

    def test_handles_runtime_error(self):
        """Test handling RuntimeError."""
        exc = RuntimeError("Runtime issue occurred")

        result = handle_evernote_error(exc)
        data = result

        assert data["success"] is False
        assert "Runtime issue occurred" in data["error"]

    def test_error_response_structure(self):
        """Test that error response has expected structure."""
        exc = EDAMUserException(
            errorCode=EDAMErrorCode.BAD_DATA_FORMAT,
        )

        result = handle_evernote_error(exc)
        data = result

        assert "success" in data
        assert data["success"] is False
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_does_not_expose_auth_token(self):
        """Test that auth tokens are redacted from error messages."""
        # Test Evernote token format: S=<signature>:<userid>:<timestamp>
        exc = Exception("Failed with token:S=123:ABC123XYZ")

        result = handle_evernote_error(exc)
        data = result

        # Token should be redacted
        assert "S=123" not in data["error"]
        assert "ABC123XYZ" not in data["error"]
        assert "[REDACTED]" in data["error"]

    def test_redacts_token_without_keyword(self):
        """Test that tokens without 'token:' prefix are also redacted."""
        exc = Exception("Authentication failed: S=456:DEF456:1234567890")

        result = handle_evernote_error(exc)
        data = result

        assert "S=456" not in data["error"]
        assert "[REDACTED]" in data["error"]

    def test_redacts_password_in_error(self):
        """Test that passwords are redacted from error messages."""
        exc = Exception("Invalid credentials with password:secret123")

        result = handle_evernote_error(exc)
        data = result

        assert "secret123" not in data["error"]
        assert "[REDACTED]" in data["error"]

    def test_does_not_redact_safe_messages(self):
        """Test that normal error messages are not affected."""
        exc = Exception("Note not found")

        result = handle_evernote_error(exc)
        data = result

        assert data["error"] == "Note not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
