"""
HTML parsing for standalone HTML files in ghmd-blog.

This module allows including standalone HTML files in the blog index
alongside markdown posts. Metadata is extracted from HTML tags.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Optional
from html.parser import HTMLParser


@dataclass
class HtmlPage:
    """Represents a standalone HTML page."""

    # Metadata
    title: str
    date: Optional[datetime] = None
    description: str = ""

    # Generated
    slug: str = ""
    source_path: Path = field(default_factory=lambda: Path())
    output_path: Path = field(default_factory=lambda: Path())

    # Mark as HTML for template differentiation
    is_html: bool = True

    @property
    def url(self) -> str:
        """Get the URL path for this HTML page (without base_url)."""
        # Convert output path to URL
        # e.g., output/pages/sample.html -> /pages/sample.html
        parts = self.output_path.parts
        if parts and parts[0] == "output":
            parts = parts[1:]
        return "/" + "/".join(parts)


class TitleExtractor(HTMLParser):
    """Extract <title> tag content from HTML."""

    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


class HtmlPageParser:
    """Parses HTML files for metadata."""

    def parse_file(self, file_path: Path, source_dir: Path) -> HtmlPage:
        """
        Parse an HTML file into an HtmlPage object.

        Args:
            file_path: Path to the HTML file
            source_dir: Root directory of blog source

        Returns:
            HtmlPage object with extracted metadata
        """
        # Read HTML content
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Extract title from <title> tag
        title_extractor = TitleExtractor()
        title_extractor.feed(html_content)
        title = title_extractor.title

        # Fallback to filename if no title found
        if not title:
            title = file_path.stem.replace("-", " ").replace("_", " ").title()

        # Extract description from meta tag (optional)
        description = ""
        desc_match = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
            html_content,
            re.IGNORECASE,
        )
        if desc_match:
            description = desc_match.group(1)

        # Use file modification time as date (keep full datetime for accurate sorting)
        file_stat = file_path.stat()
        file_date = datetime.fromtimestamp(file_stat.st_mtime)

        # Calculate slug and output path (relative to source directory)
        relative_path = file_path.relative_to(source_dir)
        slug = relative_path.stem

        return HtmlPage(
            title=title,
            date=file_date,
            description=description,
            slug=slug,
            source_path=file_path,
            output_path=relative_path,
        )
