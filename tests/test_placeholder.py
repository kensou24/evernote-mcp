"""Simple test to verify test suite works."""

import pytest


def test_placeholder():
    """Placeholder test to ensure pytest discovery works."""
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
