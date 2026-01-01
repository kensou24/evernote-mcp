# Publishing to PyPI

This guide explains how to publish the `evernote-mcp` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **API Token**: Generate an API token at https://pypi.org/manage/account/token/
   - Select "Entire account" for global access, or specific project scope
   - Copy the token (format: `pypi-xxxx...`) - it's only shown once!

## Configuration

### Configure Poetry to use the token

```bash
# Set the PyPI token in Poetry config
poetry config pypi-token.pypi <your-token-here>
```

### Alternative: Use environment variable

```bash
export POETRY_PYPI_TOKEN_PYPI="<your-token-here>"
```

## Publishing Steps

### 1. Update version (if needed)

Edit `pyproject.toml`:

```toml
[project]
version = "0.1.3"  # Increment version number
```

### 2. Build the package

```bash
# Clean previous builds
rm -rf dist/

# Build the package
poetry build
```

This creates:
- `dist/evernote_mcp-{version}-py3-none-any.whl` (wheel)
- `dist/evernote_mcp-{version}.tar.gz` (source)

### 3. Publish to PyPI

```bash
# Publish using Poetry
poetry publish
```

Or using Twine:

```bash
# Install twine
pip install twine

# Publish
twine upload dist/*
```

### 4. Verify publication

Wait a few minutes, then verify:

```bash
# Check PyPI
curl -s https://pypi.org/pypi/evernote-mcp/json | jq '.releases'

# Test installation
pip install evernote-mcp

# Or use uvx
uvx evernote-mcp --help
```

## Common Issues

### "File already exists" error

PyPI doesn't allow re-uploading files with the same name and hash. You must:
1. Increment the version number in `pyproject.toml`
2. Rebuild with `poetry build`
3. Publish again with `poetry publish`

### "Invalid authentication" error

Make sure:
- Username is set to `__token__` (two underscores)
- Password is your API token (starts with `pypi-`)

### Using TestPyPI (for testing)

First, register at https://test.pypi.org/account/register/

```bash
# Configure testpypi token
poetry config pypi-token.testpypi <your-testpypi-token>

# Publish to testpypi
poetry publish --repository testpypi

# Test installation from testpypi
pip install --index-url https://test.pypi.org/simple/ evernote-mcp
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **0.1.x**: Bug fixes
- **0.2.0**: New features (backward compatible)
- **1.0.0**: Stable release
- **2.0.0**: Breaking changes

## Quick Reference

```bash
# Complete publishing workflow
poetry version patch  # or minor, or major
rm -rf dist/
poetry build
poetry publish
```
