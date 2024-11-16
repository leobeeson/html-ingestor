"""
HTML Parser module for extracting structured content from HTML documents.

Preserves semantic structure while cleaning and normalizing text for downstream NLP tasks.
"""

import logging
import re

from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)


class HTMLParsingError(Exception):
    """Raised when there's an error parsing HTML content."""


class HtmlParser:
    """
    Parser for converting HTML documents into cleaned, structured text.

    Maintains document hierarchy and semantic elements while removing noise and normalizing format.
    """

    def parse_text_with_structure(self, main_div: Tag | NavigableString | None) -> str:
        """
        Parse HTML content preserving semantic structure of specified tags while removing others.

        Args:
            main_div: BeautifulSoup Tag, NavigableString, or None containing HTML content

        Returns:
            str: HTML string with preserved semantic tags, stripped attributes, and proper spacing

        Raises:
            HTMLScrapingError: If HTML parsing fails

        Notes:
            - Preserves: h1-h6, p, ul, ol, li, table, tr, td, th
            - Removes all other tags while keeping their content
            - Strips all HTML attributes
            - Adds newlines after block elements
        """
        if main_div is None or isinstance(main_div, NavigableString):
            return str(main_div) if main_div else ""

        try:
            soup = BeautifulSoup(str(main_div), "html.parser")
            keep_tags: list[str] = [
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "p",
                "ul",
                "ol",
                "li",
                "table",
                "tr",
                "td",
                "th",
            ]
            block_tags: list[str] = [
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "p",
                "ul",
                "ol",
                "table",
            ]

            for tag in soup.find_all(True):
                if tag.name not in keep_tags:
                    tag.unwrap()
                else:
                    tag.attrs = {}

            processed_html: str = str(soup)
            processed_html = self.clean_html(processed_html, block_tags)
            return processed_html.strip()
        except Exception as e:
            logger.error(f"Error in HTML parsing: {str(e)}")
            raise HTMLParsingError(f"Failed to process HTML: {str(e)}")

    def clean_html(self, html: str, block_tags: list[str]) -> str:
        """
        Clean HTML string by normalizing whitespace and formatting.

        Args:
            html: HTML string to clean
            block_tags: List of HTML tags to be followed by newlines

        Returns:
            str: Cleaned HTML with normalized spacing and formatting

        Notes:
            - Normalizes newlines
            - Trims whitespace from line ends
            - Adds newlines after block tags
            - Removes divs
            - Converts Unicode spaces to regular spaces
            - Removes control/format characters
        """
        html = re.sub(r"\n+", "\n", html)
        html = re.sub(r"^\s+|\s+$", "", html, flags=re.MULTILINE)
        html = re.sub(
            r"(<(?:"
            + "|".join(block_tags)
            + r")[^>]*>)(.+?)(</(?:"
            + "|".join(block_tags)
            + r")>)",
            r"\1\2\3\n",
            html,
            flags=re.DOTALL,
        )
        html = re.sub(r"<li>(.+?)</li>", r"<li>\1</li>\n", html)
        html = re.sub(r"<div[^>]*>|</div>", "", html)
        html = re.sub(r"\n+", "\n", html)
        # First replace separators with spaces
        html = re.sub(r"[\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]", " ", html)
        # Then remove format/control chars
        html = re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\u200B-\u200F\u202A-\u202E\uFEFF]",
            "",
            html,
        )
        # Collapse multiple spaces into single space
        html = re.sub(r" +", " ", html)
        return html
