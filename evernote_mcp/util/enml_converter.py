"""ENML to text/markdown conversion utilities."""
import re
import html


def enml_to_text(enml_content: str) -> str:
    """Convert ENML content to plain text.

    Args:
        enml_content: ENML format content

    Returns:
        Plain text content
    """
    # Remove all XML/HTML tags
    text = re.sub(r'<[^>]+>', ' ', enml_content)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def enml_to_markdown(enml_content: str) -> str:
    """Convert ENML content to Markdown format.

    Args:
        enml_content: ENML format content

    Returns:
        Markdown formatted content
    """
    import xml.etree.ElementTree as ET

    # Basic ENML to Markdown conversion
    content = enml_content

    # Convert checkboxes
    content = re.sub(r'<en-todo[^>]*/>', '- [ ] ', content)
    content = re.sub(r'<en-todo[^>]*checked="true"[^>]*/>', '- [x] ', content)

    # Remove media placeholders
    content = re.sub(r'<en-media[^>]*/>', '[Media]', content)
    content = re.sub(r'<en-crypt[^>]*>.*?</en-crypt>', '[Encrypted]', content, flags=re.DOTALL)

    # Convert basic formatting
    content = re.sub(r'<b>(.*?)</b>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<i>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<em>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<u>(.*?)</u>', r'_\1_', content, flags=re.DOTALL)

    # Convert links
    content = re.sub(r'<a href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content)

    # Convert div and br to newlines
    content = re.sub(r'<div[^>]*>', '\n', content)
    content = re.sub(r'</div>', '\n', content)
    content = re.sub(r'<br\s*/?>', '\n', content)

    # Remove remaining tags
    text = enml_to_text(content)

    return text


def text_to_enml(text: str, title: str = "") -> str:
    """Convert plain text to ENML format.

    Args:
        text: Plain text content
        title: Optional note title

    Returns:
        ENML formatted content
    """
    # Escape HTML special characters
    content = html.escape(text)

    # Convert newlines to <br> or <div>
    content = content.replace('\n', '<br/>')

    # Build ENML document
    enml = f'<?xml version="1.0" encoding="UTF-8"?>\n'
    enml += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n'
    enml += '<en-note>'
    enml += content
    enml += '</en-note>'

    return enml
