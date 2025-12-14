"""
Markdown parsing with frontmatter extraction for ghmd-blog.
"""

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import frontmatter
import markdown
from markdown.extensions.toc import TocExtension
from pymdownx import superfences, highlight


@dataclass
class Post:
    """Represents a parsed blog post."""

    # From frontmatter
    title: str
    date: Optional[date] = None
    update: Optional[date] = None
    description: str = ""
    author: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    draft: bool = False
    toc_enabled: Optional[bool] = None  # None means use global setting
    exclude_from_index: bool = False  # Exclude from blog index
    template: str = "post"  # Template to use: "post" or "page"

    # Generated
    content_html: str = ""
    toc_html: str = ""
    slug: str = ""
    source_path: Path = field(default_factory=lambda: Path())
    output_path: Path = field(default_factory=lambda: Path())
    reading_time: int = 0  # minutes
    headings: list[dict] = field(default_factory=list)

    @property
    def url(self) -> str:
        """Get the URL path for this post (without base_url)."""
        # Convert output path to URL
        # e.g., output/tutorials/intro.html -> /tutorials/intro.html
        parts = self.output_path.parts
        if parts and parts[0] == "output":
            parts = parts[1:]
        return "/" + "/".join(parts)


class MarkdownParser:
    """Parses markdown files with frontmatter into Post objects."""

    # Average reading speed (words per minute)
    WORDS_PER_MINUTE = 200

    def __init__(self):
        """Initialize the markdown parser with extensions."""
        self.md = markdown.Markdown(
            extensions=[
                "meta",
                TocExtension(
                    permalink=False,
                    toc_depth="2-4",
                ),
                "tables",
                "fenced_code",
                "codehilite",
                "attr_list",
                "def_list",
                "footnotes",
                "md_in_html",
                "pymdownx.superfences",
                "pymdownx.highlight",
                "pymdownx.inlinehilite",
                "pymdownx.magiclink",
                "pymdownx.tasklist",
                "pymdownx.mark",
                "pymdownx.tilde",
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "guess_lang": False,
                },
                "pymdownx.highlight": {
                    "css_class": "highlight",
                    "guess_lang": False,
                },
                "pymdownx.superfences": {
                    "custom_fences": [],
                },
            },
        )

    def parse_file(self, file_path: Path, source_dir: Path) -> Post:
        """
        Parse a markdown file into a Post object.

        Args:
            file_path: Path to the markdown file.
            source_dir: Root source directory (for calculating relative paths).

        Returns:
            Parsed Post object.
        """
        # Read and parse frontmatter
        with open(file_path, "r", encoding="utf-8") as f:
            post_data = frontmatter.load(f)

        # Extract frontmatter fields
        title = post_data.get("title", file_path.stem.replace("-", " ").title())
        
        # Handle date parsing
        date_val = post_data.get("date")
        if isinstance(date_val, datetime):
            parsed_date = date_val.date()
        elif isinstance(date_val, date):
            parsed_date = date_val
        elif isinstance(date_val, str):
            try:
                parsed_date = datetime.strptime(date_val, "%Y-%m-%d").date()
            except ValueError:
                parsed_date = None
        else:
            parsed_date = None

        # Handle update date parsing
        update_val = post_data.get("update")
        if isinstance(update_val, datetime):
            parsed_update = update_val.date()
        elif isinstance(update_val, date):
            parsed_update = update_val
        elif isinstance(update_val, str):
            try:
                parsed_update = datetime.strptime(update_val, "%Y-%m-%d").date()
            except ValueError:
                parsed_update = None
        else:
            parsed_update = None

        description = post_data.get("description", "")
        author = post_data.get("author")  # None if not specified
        tags = post_data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        draft = post_data.get("draft", False)
        toc_enabled = post_data.get("toc")  # None if not specified
        exclude_from_index = post_data.get("exclude_from_index", False)
        template = post_data.get("template", "post").lower()

        # Validate template
        if template not in ["post", "page"]:
            print(f"Warning: Invalid template '{template}' in {file_path}, defaulting to 'post'")
            template = "post"

        # Reset markdown parser state
        self.md.reset()

        # Convert markdown to HTML
        content_html = self.md.convert(post_data.content)

        # Get TOC (generated by TocExtension)
        toc_html = getattr(self.md, "toc", "")
        
        # Extract headings for TOC decision
        headings = self._extract_headings(content_html)

        # Calculate reading time
        word_count = len(post_data.content.split())
        reading_time = max(1, round(word_count / self.WORDS_PER_MINUTE))

        # Calculate slug and output path
        relative_path = file_path.relative_to(source_dir)
        slug = relative_path.stem
        output_path = relative_path.with_suffix(".html")

        return Post(
            title=title,
            date=parsed_date,
            update=parsed_update,
            description=description,
            author=author,
            tags=tags,
            draft=draft,
            toc_enabled=toc_enabled,
            exclude_from_index=exclude_from_index,
            template=template,
            content_html=content_html,
            toc_html=toc_html,
            slug=slug,
            source_path=file_path,
            output_path=output_path,
            reading_time=reading_time,
            headings=headings,
        )

    def _extract_headings(self, html: str) -> list[dict]:
        """Extract headings from HTML for TOC generation."""
        headings = []
        # Match h2, h3, h4 tags with their id and content
        pattern = r'<h([2-4])[^>]*id="([^"]*)"[^>]*>(.*?)</h\1>'
        
        for match in re.finditer(pattern, html, re.DOTALL):
            level = int(match.group(1))
            heading_id = match.group(2)
            # Strip HTML tags from heading text
            text = re.sub(r"<[^>]+>", "", match.group(3)).strip()
            # Remove pilcrow/paragraph symbol that TOC extension adds (both forms)
            text = text.replace("¶", "").replace("&para;", "").strip()
            headings.append({
                "level": level,
                "id": heading_id,
                "text": text,
            })
        
        return headings

    def should_show_toc(self, post: Post, global_setting: bool, min_headings: int) -> bool:
        """
        Determine if TOC should be shown for a post.

        Args:
            post: The post to check.
            global_setting: Global show_toc config value.
            min_headings: Minimum headings required to show TOC.

        Returns:
            True if TOC should be displayed.
        """
        # Post-level override takes precedence
        if post.toc_enabled is not None:
            if not post.toc_enabled:
                return False
            # If post explicitly enables TOC, still check min_headings
            return len(post.headings) >= min_headings

        # Use global setting
        if not global_setting:
            return False

        return len(post.headings) >= min_headings
