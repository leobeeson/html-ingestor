"""
This module contains unit tests for the HtmlParser class in the html_ingestor.parsers.html_parser module.

The tests are designed to verify the functionality of the clean_html and parse_text_with_structure methods.

Fixtures:
    scraper: Provides an instance of HtmlParser for use in tests.
    block_tags: Provides a list of HTML block tags for use in tests.

Test Classes:
    TestHtmlCleanup: Contains tests for the clean_html method.
        - test_removes_multiple_consecutive_newlines: Verifies that multiple consecutive newlines are removed.
        - test_removes_leading_trailing_whitespace_per_line: Verifies that leading and trailing whitespace per line is removed.
        - test_adds_newline_after_block_elements: Verifies that a newline is added after block elements.
        - test_adds_newline_after_list_items: Verifies that a newline is added after list items.
        - test_unicode_character_handling: Verifies that various Unicode characters are handled correctly.
        - test_multilingual_text_handling: Verifies that multilingual text is handled correctly.
        - test_handles_nested_elements: Verifies that nested elements are handled correctly.
        - test_handles_empty_input: Verifies that empty input is handled correctly.
        - test_handles_complex_html_structure: Verifies that complex HTML structures are handled correctly.
        - test_preserves_block_tag_content_with_special_characters: Verifies that block tag content with special characters is preserved.

    TestParseTextWithStructure: Contains tests for the parse_text_with_structure method.
        - test_handles_none_input: Verifies that None input is handled correctly.
        - test_handles_navigable_string: Verifies that NavigableString input is handled correctly.
        - test_unwraps_non_keep_tags: Verifies that non-keep tags are unwrapped.
        - test_strips_tag_attributes: Verifies that tag attributes are stripped.
        - test_keeps_specified_tags: Verifies that specified tags are kept.
        - test_preserves_nested_keep_tags: Verifies that nested keep tags are preserved.
        - test_handles_mixed_content: Verifies that mixed content is handled correctly.
        - test_raises_html_scraping_error: Verifies that an HTMLParsingError is raised for broken tags.
"""

import pytest
from bs4 import BeautifulSoup, NavigableString, Tag

from html_ingestor.parsers.html_parser import HtmlParser, HTMLParsingError


@pytest.fixture
def scraper() -> HtmlParser:
    return HtmlParser()


@pytest.fixture
def block_tags() -> list[str]:
    return ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table"]


class TestHtmlCleanup:

    @pytest.mark.parametrize(
        "input_html, expected",
        [
            ("line1\n\n\nline2", "line1\nline2"),
            ("\n\n  \n", ""),
            ("single\n", "single"),
        ],
    )
    def test_removes_multiple_consecutive_newlines(
        self, scraper: HtmlParser, block_tags: list[str], input_html: str, expected: str
    ) -> None:
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    @pytest.mark.parametrize(
        "input_html, expected",
        [
            ("  start  ", "start"),
            ("  line1  \n  line2  ", "line1\nline2"),
            ("\t\tindented\t\t", "indented"),
        ],
    )
    def test_removes_leading_trailing_whitespace_per_line(
        self, scraper: HtmlParser, block_tags: list[str], input_html: str, expected: str
    ) -> None:
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    @pytest.mark.parametrize(
        "input_html, expected",
        [
            ("<p>text</p>", "<p>text</p>\n"),
            ("<h1>header</h1>", "<h1>header</h1>\n"),
            ("<table>data</table>", "<table>data</table>\n"),
        ],
    )
    def test_adds_newline_after_block_elements(
        self, scraper: HtmlParser, block_tags: list[str], input_html: str, expected: str
    ) -> None:
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    @pytest.mark.parametrize(
        "input_html, expected",
        [
            ("<li>item</li>", "<li>item</li>\n"),
            ("<li>item1</li><li>item2</li>", "<li>item1</li>\n<li>item2</li>\n"),
            ("<ul><li>nested</li></ul>", "<ul><li>nested</li>\n</ul>\n"),
        ],
    )
    def test_adds_newline_after_list_items(
        self, scraper: HtmlParser, block_tags: list[str], input_html: str, expected: str
    ) -> None:
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    @pytest.mark.parametrize(
        "input_html, expected",
        [
            # Spaces that should become single space
            ("price\u2000cost", "price cost"),  # En quad space
            ("price\u2002cost", "price cost"),  # En space
            ("price\u2003cost", "price cost"),  # Em space
            ("item\u2029price", "item price"),  # Paragraph separator
            ("item\u2028price", "item price"),  # Line separator
            # Multiple consecutive spaces should become single space
            ("price\u2000\u2001\u2002cost", "price cost"),
            ("item\u2028\u2029price", "item price"),
            # Control/Format characters in real scenarios
            ("info\uFEFF@email.com", "info@email.com"),  # BOM in email
            ("\x07System Alert\x07", "System Alert"),  # Bell chars in alerts
            (
                "https\u200B://website.com",
                "https://website.com",
            ),  # Zero-width space in URL
            (
                "long-word-break\u200Bable-term",
                "long-word-breakable-term",
            ),  # Zero-width space used for word breaking
            # Real-world mixed scenarios
            (
                "Samsung\u200B\u2000Electronics",
                "Samsung Electronics",
            ),  # Company name with formatting
            (
                "Tel\u2003:\u20031234",
                "Tel : 1234",
            ),  # Em spaces around colon from PDF conversion
            (
                "US$\u2009500",
                "US$ 500",
            ),  # Thin space after currency from financial docs
            # Scientific/Math notation
            ("25\u2009kg", "25 kg"),  # Thin space for unit
            ("E\u2009=\u2009mc²", "E = mc²"),  # Thin spaces around equals
            ("100\u2009°C", "100 °C"),  # Thin space for temperature
            # Technical standards/references
            ("IEEE\u2009802.11ac", "IEEE 802.11ac"),  # Standards notation
            ("10\u2009+\u2009\u200B5", "10 + 5"),  # Math expression
            ("Fig.\u200912", "Fig. 12"),  # Figure reference
            # CJK text spacing (Common in Asian typography)
            ("東京\u3000スカイツリー", "東京 スカイツリー"),  # Ideographic space
            ("スーパー\u200B市場", "スーパー市場"),  # Zero-width space in Japanese
            # Multiple consecutive spaces
            ("Too    many    spaces", "Too many spaces"),
            ("Mixed\u2009\u2002\u3000spaces", "Mixed spaces"),
            # Mixed control characters and spaces
            (
                "data\u200B\u2000mining",
                "data mining",
            ),  # Should cleanup to normal compound
            ("AI\u200B\u2009+\u200B\u2009ML", "AI + ML"),  # Technical term spacing
            # HTML content
            ("<p>Para 1\u2028next line</p>", "<p>Para 1 next line</p>\n"),
            ("<h1>Title\u2002Here</h1>", "<h1>Title Here</h1>\n"),
            # Edge cases
            ("\u200B\u2000\u200B", " "),  # Only special characters
            (
                "word\u200B\u2000",
                "word",
            ),  # Special characters at end, though removed by `html = re.sub(r'^\s+|\s+$', '', html, flags=re.MULTILINE)`
            ("\u200B\u2000word", " word"),  # Special characters at start
        ],
    )
    def test_unicode_character_handling(
        self, scraper: HtmlParser, block_tags: list[str], input_html: str, expected: str
    ) -> None:
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    @pytest.mark.parametrize(
        "input_html, expected",
        [
            # Hebrew
            ("מדעי המחשב", "מדעי המחשב"),  # Computer Science
            # Spanish with accents
            ("¿Cómo estás?", "¿Cómo estás?"),  # How are you?
            ("El niño", "El niño"),  # The boy
            # French with accents/ligatures
            ("C'est l'été", "C'est l'été"),  # It's summer
            ("Œuvre complète", "Œuvre complète"),  # Complete works
            # German with umlauts/eszett
            ("Straße", "Straße"),  # Street
            ("München", "München"),  # Munich
            # Japanese (mixed scripts)
            ("東京タワー", "東京タワー"),  # Tokyo Tower
            ("ラーメン屋", "ラーメン屋"),  # Ramen shop
            # Korean with spaces
            ("안녕 하세요", "안녕 하세요"),  # Hello
            # Chinese (no spaces needed)
            ("北京市", "北京市"),  # Beijing city
            # Mixed languages in one document
            ("<p>Tokyo (東京) Tower</p>", "<p>Tokyo (東京) Tower</p>\n"),
            ("<h1>Café de パリ</h1>", "<h1>Café de パリ</h1>\n"),
            # Copy-pasted from PDFs/Word docs with special spaces
            (
                "Tokyo\u2003東京\u2002Tower",
                "Tokyo 東京 Tower",
            ),  # Em spaces from formatted docs
            (
                "Café\u2009de\u2009パリ",
                "Café de パリ",
            ),  # Thin spaces from design software
            ("Café\u2005de\u200Aパリ", "Café de パリ"),  # Medium and hair space
            # Zero-width space in mixed text (common in converted documents)
            (
                "New\u2004York・ニューヨーク",
                "New York・ニューヨーク",
            ),  # Japanese middle dot preserved
            (
                "Berlin\u2006|\u205F베를린",
                "Berlin | 베를린",
            ),  # Six-per-em and math space
            # Documents with BOM and other control chars
            ("\uFEFFעברית\u2007text", "עברית text"),  # Hebrew-English with BOM
            ("русский\u2001text", "русский text"),  # Mixed scripts with zero-width
            # Multiple space types in formal documents
            ("Prix\u2002:\u20095\u3000€", "Prix : 5 €"),  # French pricing
            (
                "Tel\u200A:\u2000(03)\u20081234",
                "Tel : (03) 1234",
            ),  # International phone format
        ],
    )
    def test_multilingual_text_handling(
        self, scraper: HtmlParser, block_tags: list[str], input_html: str, expected: str
    ) -> None:
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    def test_handles_nested_elements(
        self, scraper: HtmlParser, block_tags: list[str]
    ) -> None:
        input_html = "<div><p>First paragraph</p><p>Second paragraph</p></div>"
        expected = "<p>First paragraph</p>\n<p>Second paragraph</p>\n"
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    def test_handles_empty_input(
        self, scraper: HtmlParser, block_tags: list[str]
    ) -> None:
        assert scraper.clean_html("", block_tags) == ""

    def test_handles_complex_html_structure(
        self, scraper: HtmlParser, block_tags: list[str]
    ) -> None:
        input_html = "<div class='wrapper'><h1>Title</h1><p>First paragraph</p><ul><li>Item 1</li><li>Item 2</li></ul><table><tr><td>Data</td></tr></table></div>"
        expected = (
            "<h1>Title</h1>\n"
            "<p>First paragraph</p>\n"
            "<ul><li>Item 1</li>\n"
            "<li>Item 2</li>\n"
            "</ul>\n"
            "<table><tr><td>Data</td></tr></table>\n"
        )
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected

    def test_preserves_block_tag_content_with_special_characters(
        self, scraper: HtmlParser, block_tags: list[str]
    ) -> None:
        input_html = "<p>Line 1 & Line 2 > Line 3 < Line 4</p>"
        expected = "<p>Line 1 & Line 2 > Line 3 < Line 4</p>\n"
        result: str = scraper.clean_html(input_html, block_tags)
        assert result == expected


class TestParseTextWithStructure:

    def test_handles_none_input(self, scraper: HtmlParser) -> None:
        assert scraper.parse_text_with_structure(None) == ""

    def test_handles_navigable_string(self, scraper: HtmlParser) -> None:
        nav_string = NavigableString("Simple text")
        assert scraper.parse_text_with_structure(nav_string) == "Simple text"

    def test_unwraps_non_keep_tags(self, scraper: HtmlParser) -> None:
        soup = BeautifulSoup("<div><span>Keep this text</span></div>", "html.parser")
        assert scraper.parse_text_with_structure(soup.div) == "Keep this text"

    def test_strips_tag_attributes(self, scraper: HtmlParser) -> None:
        soup = BeautifulSoup(
            '<p class="important" style="color: red;">Text</p>', "html.parser"
        )
        assert scraper.parse_text_with_structure(soup.p) == "<p>Text</p>"

    def test_keeps_specified_tags(self, scraper: HtmlParser) -> None:
        html = """
            <article>
                <h1>Title</h1>
                <div>
                    <p>Para</p>
                    <span>Keep content</span>
                    <ul><li>Item</li></ul>
                </div>
            </article>
        """
        soup = BeautifulSoup(html, "html.parser")
        expected = "<h1>Title</h1>\n<p>Para</p>\nKeep content\n<ul><li>Item</li>\n</ul>"
        assert scraper.parse_text_with_structure(soup.article) == expected

    def test_preserves_nested_keep_tags(self, scraper: HtmlParser) -> None:
        html = "<div><table><tr><th>Header</th><td>Data</td></tr></table></div>"
        soup = BeautifulSoup(html, "html.parser")
        expected = "<table><tr><th>Header</th><td>Data</td></tr></table>"
        assert scraper.parse_text_with_structure(soup.div) == expected

    def test_handles_mixed_content(self, scraper: HtmlParser) -> None:
        html = """
            <div>
                Text before
                <p>Paragraph</p>
                <span>Unwrapped span</span>
                <h2>Header</h2>
                Text after
            </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        expected = (
            "Text before\n<p>Paragraph</p>\nUnwrapped span\n<h2>Header</h2>\nText after"
        )
        assert scraper.parse_text_with_structure(soup.div) == expected

    def test_raises_html_scraping_error(self, scraper: HtmlParser) -> None:
        class BrokenTag(Tag):
            def __str__(self) -> str:
                raise Exception("Simulated parsing error")

        with pytest.raises(HTMLParsingError) as exc_info:
            scraper.parse_text_with_structure(BrokenTag(name="broken"))
        assert "Failed to process HTML" in str(exc_info.value)
