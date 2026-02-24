"""Error handling utilities for Evernote MCP server."""
import logging
import re
from typing import Any, Dict
from evernote.edam.error.ttypes import (
    EDAMErrorCode,
    EDAMNotFoundException,
    EDAMSystemException,
    EDAMUserException,
)

logger = logging.getLogger(__name__)

# Pattern to match Evernote auth tokens in error messages
# Format: S=<signature>:<userid>:<timestamp> etc.
_AUTH_TOKEN_PATTERN = re.compile(
    r'(token[:\s]*)?S=[\w:/=+-]+',
    re.IGNORECASE
)


def _redact_sensitive_info(message: str) -> str:
    """Redact sensitive information (auth tokens, passwords) from error messages.

    Args:
        message: Original error message

    Returns:
        Error message with sensitive info redacted
    """
    # First redact Evernote auth tokens (S=...)
    message = _AUTH_TOKEN_PATTERN.sub('[REDACTED]', message)

    # Then redact common password/secret patterns
    # Use word boundaries to avoid matching "token" in "Authentication"
    message = re.sub(r'(?i)(password|secret|api_key)([:\s][^\s\'"]+)?',
                     r'\1: [REDACTED]', message)

    # Avoid redacting "token" when it's part of a legitimate error message
    # Only redact if it looks like a value assignment (token: value or token=value)
    # This prevents redacting "Invalid authentication token"
    message = re.sub(r'(?i)(auth\s*token|bearer\s*token)([:\s=][^\s\'"]+)?',
                     r'\1: [REDACTED]', message)

    return message


def handle_evernote_error(e: Exception) -> Dict[str, Any]:
    """Convert Evernote API exceptions to standardized error responses.

    Args:
        e: The exception to handle

    Returns:
        Dictionary with success=False and error details (with sensitive info redacted)
    """
    if isinstance(e, EDAMUserException):
        error_message = _get_edam_user_error_message(e)
        logger.error(f"EDAMUserException: {error_message}")
        return {
            "success": False,
            "error": _redact_sensitive_info(error_message),
            "error_code": e.errorCode,
        }
    elif isinstance(e, EDAMSystemException):
        logger.error(f"EDAMSystemException: {e.message}")
        return {
            "success": False,
            "error": _redact_sensitive_info(f"System error: {e.message}"),
            "error_code": e.errorCode,
        }
    elif isinstance(e, EDAMNotFoundException):
        logger.error(f"EDAMNotFoundException: {e.identifier}")
        return {
            "success": False,
            "error": f"Resource not found: {e.identifier}",
        }
    else:
        error_msg = str(e)
        logger.error(f"Unexpected error: {type(e).__name__}: {_redact_sensitive_info(error_msg)}")
        return {
            "success": False,
            "error": _redact_sensitive_info(error_msg),
        }


def _get_edam_user_error_message(e: EDAMUserException) -> str:
    """Convert EDAMUserException to human-readable message.

    Args:
        e: EDAMUserException

    Returns:
        Human-readable error message (without sensitive parameter details)
    """
    error_messages = {
        EDAMErrorCode.BAD_DATA_FORMAT: "Invalid data format",
        EDAMErrorCode.DATA_CONFLICT: "Data conflict - resource already exists",
        EDAMErrorCode.DATA_REQUIRED: "Required data is missing",
        EDAMErrorCode.ENML_VALIDATION: "Invalid note content format",
        EDAMErrorCode.LIMIT_REACHED: "Account limit reached",
        EDAMErrorCode.QUOTA_REACHED: "Upload quota reached",
        EDAMErrorCode.PERMISSION_DENIED: "Permission denied",
        EDAMErrorCode.AUTH_EXPIRED: "Authentication token expired",
        EDAMErrorCode.INVALID_AUTH: "Invalid authentication token",
    }

    base_message = error_messages.get(e.errorCode, f"Unknown error (code: {e.errorCode})")

    # Note: We no longer include the parameter in the error message to avoid
    # leaking internal implementation details or potentially sensitive data

    return base_message
