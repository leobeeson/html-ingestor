"""Core functionality for HTML document ingestion and processing."""


def parse_html(html_content: str) -> dict[str, str]:
    """
    Parse HTML content and return structured data.

    Args:
        html_content: Raw HTML string to parse.

    Returns:
        Dictionary containing parsed HTML data.
    """
    return {"content": html_content}  # Placeholder implementation
