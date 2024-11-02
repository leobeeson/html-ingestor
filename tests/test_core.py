"""Test cases for the core HTML ingestion functionality."""

from html_ingestor.core import parse_html


def test_parse_html_returns_dict() -> None:
    """Test that parse_html returns a dictionary."""
    html = "<html><body>Test</body></html>"
    result = parse_html(html)
    assert isinstance(result, dict)
    assert "content" in result
