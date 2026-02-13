"""Error handling utilities for Evernote MCP server."""
import logging
from typing import Any, Dict
from evernote.edam.error.ttypes import (
    EDAMErrorCode,
    EDAMNotFoundException,
    EDAMSystemException,
    EDAMUserException,
)

logger = logging.getLogger(__name__)


def handle_evernote_error(e: Exception) -> Dict[str, Any]:
    """Convert Evernote API exceptions to standardized error responses.

    Args:
        e: The exception to handle

    Returns:
        Dictionary with success=False and error details
    """
    if isinstance(e, EDAMUserException):
        error_message = _get_edam_user_error_message(e)
        logger.error(f"EDAMUserException: {error_message}")
        return {
            "success": False,
            "error": error_message,
            "error_code": e.errorCode,
            "parameter": getattr(e, 'parameter', None)
        }
    elif isinstance(e, EDAMSystemException):
        logger.error(f"EDAMSystemException: {e.message}")
        return {
            "success": False,
            "error": f"System error: {e.message}",
            "error_code": e.errorCode,
        }
    elif isinstance(e, EDAMNotFoundException):
        logger.error(f"EDAMNotFoundException: {e.identifier}")
        return {
            "success": False,
            "error": f"Resource not found: {e.identifier}",
        }
    else:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        return {
            "success": False,
            "error": str(e),
        }


def _get_edam_user_error_message(e: EDAMUserException) -> str:
    """Convert EDAMUserException to human-readable message.

    Args:
        e: EDAMUserException

    Returns:
        Human-readable error message
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

    parameter = getattr(e, 'parameter', None)
    if parameter:
        return f"{base_message}: {parameter}"

    return base_message
