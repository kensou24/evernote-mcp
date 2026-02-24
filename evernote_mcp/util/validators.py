"""Input validation utilities for Evernote MCP server."""
from typing import Optional, List


# Maximum limits for inputs
MAX_TITLE_LENGTH = 255
MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10MB in bytes
MAX_ENML_CONTENT_SIZE = 50 * 1024 * 1024  # 50MB for ENML (Evernote limit)
MAX_TAGS_PER_NOTE = 100
MAX_SEARCH_QUERY_LENGTH = 1000
MAX_NOTEBOOK_NAME_LENGTH = 100
MAX_TAG_NAME_LENGTH = 100
MAX_SAVED_SEARCH_NAME_LENGTH = 100
MAX_SAVED_SEARCH_QUERY_LENGTH = 1000
DEFAULT_LIMIT = 100
MAX_LIMIT = 250


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


def validate_title(title: str, max_length: int = MAX_TITLE_LENGTH) -> None:
    """Validate note title.

    Args:
        title: Title to validate
        max_length: Maximum allowed length

    Raises:
        ValidationError: If title is invalid
    """
    if not title:
        raise ValidationError("Title cannot be empty")
    if len(title) > max_length:
        raise ValidationError(f"Title too long (max {max_length} characters)")


def validate_content(content: str, is_enml: bool = False) -> None:
    """Validate note content size.

    Args:
        content: Content to validate
        is_enml: Whether content is ENML format (has higher limit)

    Raises:
        ValidationError: If content is too large
    """
    max_size = MAX_ENML_CONTENT_SIZE if is_enml else MAX_CONTENT_SIZE
    size = len(content.encode('utf-8'))

    if size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise ValidationError(f"Content too large (max {max_mb:.0f}MB)")


def validate_tags(tags: Optional[List[str]]) -> None:
    """Validate tag list.

    Args:
        tags: List of tag names

    Raises:
        ValidationError: If tags are invalid
    """
    if tags is None:
        return

    if len(tags) > MAX_TAGS_PER_NOTE:
        raise ValidationError(f"Too many tags (max {MAX_TAGS_PER_NOTE})")

    for tag in tags:
        if not tag:
            raise ValidationError("Tag names cannot be empty")
        if len(tag) > MAX_TAG_NAME_LENGTH:
            raise ValidationError(f"Tag name too long (max {MAX_TAG_NAME_LENGTH} characters)")


def validate_search_query(query: str) -> None:
    """Validate search query.

    Args:
        query: Search query string

    Raises:
        ValidationError: If query is invalid
    """
    if len(query) > MAX_SEARCH_QUERY_LENGTH:
        raise ValidationError(f"Search query too long (max {MAX_SEARCH_QUERY_LENGTH} characters)")


def validate_notebook_name(name: str) -> None:
    """Validate notebook name.

    Args:
        name: Notebook name

    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError("Notebook name cannot be empty")
    if len(name) > MAX_NOTEBOOK_NAME_LENGTH:
        raise ValidationError(f"Notebook name too long (max {MAX_NOTEBOOK_NAME_LENGTH} characters)")


def validate_limit(limit: int) -> None:
    """Validate result limit parameter.

    Args:
        limit: Maximum number of results

    Raises:
        ValidationError: If limit is invalid
    """
    if limit < 1:
        raise ValidationError("Limit must be at least 1")
    if limit > MAX_LIMIT:
        raise ValidationError(f"Limit too large (max {MAX_LIMIT})")


def validate_guid(guid: str, guid_type: str = "resource") -> None:
    """Validate Evernote GUID format.

    Args:
        guid: GUID string to validate
        guid_type: Type of GUID (for error message)

    Raises:
        ValidationError: If GUID is invalid
    """
    if not guid:
        raise ValidationError(f"{guid_type} GUID cannot be empty")
    # Evernote GUIDs are typically hex strings, 32+ chars
    if len(guid) < 30:
        raise ValidationError(f"Invalid {guid_type} GUID format")
