"""Unit tests for input validation utilities."""

import pytest

from evernote_mcp.util.validators import (
    ValidationError,
    validate_title,
    validate_content,
    validate_tags,
    validate_search_query,
    validate_limit,
    validate_notebook_name,
)


class TestValidateTitle:
    """Test title validation."""

    def test_accepts_valid_title(self):
        """Test that valid titles are accepted."""
        validate_title("My Note Title")  # Should not raise

    def test_rejects_empty_title(self):
        """Test that empty titles are rejected."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_title("")

    def test_rejects_long_title(self):
        """Test that titles exceeding max length are rejected."""
        long_title = "a" * 256
        with pytest.raises(ValidationError, match="too long"):
            validate_title(long_title)

    def test_accepts_max_length_title(self):
        """Test that titles at max length are accepted."""
        max_title = "a" * 255
        validate_title(max_title)  # Should not raise


class TestValidateContent:
    """Test content validation."""

    def test_accepts_normal_content(self):
        """Test that normal content is accepted."""
        content = "This is a normal note content."
        validate_content(content)  # Should not raise

    def test_rejects_large_text_content(self):
        """Test that content exceeding limit is rejected."""
        # Create content larger than 10MB
        large_content = "a" * (10 * 1024 * 1024 + 1)
        with pytest.raises(ValidationError, match="too large"):
            validate_content(large_content)

    def test_accepts_large_enml_content(self):
        """Test that ENML content has higher limit."""
        # ENML can be up to 50MB
        large_enml = "<en-note>" + "a" * (10 * 1024 * 1024) + "</en-note>"
        validate_content(large_enml, is_enml=True)  # Should not raise


class TestValidateTags:
    """Test tag validation."""

    def test_accepts_no_tags(self):
        """Test that None is accepted for tags."""
        validate_tags(None)  # Should not raise

    def test_accepts_valid_tags(self):
        """Test that valid tag lists are accepted."""
        validate_tags(["tag1", "tag2", "tag3"])  # Should not raise

    def test_rejects_too_many_tags(self):
        """Test that too many tags are rejected."""
        tags = [f"tag{i}" for i in range(101)]
        with pytest.raises(ValidationError, match="Too many tags"):
            validate_tags(tags)

    def test_accepts_max_tags(self):
        """Test that max number of tags is accepted."""
        tags = [f"tag{i}" for i in range(100)]
        validate_tags(tags)  # Should not raise

    def test_rejects_empty_tag_name(self):
        """Test that empty tag names are rejected."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_tags(["valid", ""])

    def test_rejects_long_tag_name(self):
        """Test that long tag names are rejected."""
        with pytest.raises(ValidationError, match="too long"):
            validate_tags(["a" * 101])


class TestValidateSearchQuery:
    """Test search query validation."""

    def test_accepts_normal_query(self):
        """Test that normal queries are accepted."""
        validate_search_query("intitle:meeting")  # Should not raise

    def test_rejects_long_query(self):
        """Test that long queries are rejected."""
        long_query = "a" * 1001
        with pytest.raises(ValidationError, match="too long"):
            validate_search_query(long_query)

    def test_accepts_max_length_query(self):
        """Test that max length query is accepted."""
        max_query = "a" * 1000
        validate_search_query(max_query)  # Should not raise


class TestValidateLimit:
    """Test limit validation."""

    def test_accepts_normal_limit(self):
        """Test that normal limits are accepted."""
        validate_limit(10)  # Should not raise
        validate_limit(100)  # Should not raise

    def test_rejects_zero_limit(self):
        """Test that zero is rejected."""
        with pytest.raises(ValidationError, match="at least 1"):
            validate_limit(0)

    def test_rejects_negative_limit(self):
        """Test that negative limits are rejected."""
        with pytest.raises(ValidationError, match="at least 1"):
            validate_limit(-1)

    def test_rejects_large_limit(self):
        """Test that limits above max are rejected."""
        with pytest.raises(ValidationError, match="too large"):
            validate_limit(251)

    def test_accepts_max_limit(self):
        """Test that max limit is accepted."""
        validate_limit(250)  # Should not raise


class TestValidateNotebookName:
    """Test notebook name validation."""

    def test_accepts_valid_name(self):
        """Test that valid names are accepted."""
        validate_notebook_name("My Notebook")  # Should not raise

    def test_rejects_empty_name(self):
        """Test that empty names are rejected."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_notebook_name("")

    def test_rejects_long_name(self):
        """Test that long names are rejected."""
        with pytest.raises(ValidationError, match="too long"):
            validate_notebook_name("a" * 101)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
