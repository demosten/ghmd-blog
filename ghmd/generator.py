"""
Static site generator for ghmd-blog.
"""

import re
import shutil
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Union

from jinja2 import Environment, FileSystemLoader, PackageLoader, ChoiceLoader, select_autoescape

from .config import Config
from .parser import MarkdownParser, Post
from .html_parser import HtmlPageParser, HtmlPage
from .toc import generate_toc_html


def _slugify_tag(tag: str) -> str:
    """
    Convert a tag name to a URL-safe slug.

    Examples:
        "Python" → "python"
        "Machine Learning" → "machine-learning"
        "C++" → "c-plus-plus"
        "C#" → "c-sharp"
        ".NET" → "dotnet"

    Args:
        tag: Tag name to convert.

    Returns:
        URL-safe slug.
    """
    # Handle special cases
    tag_lower = tag.lower()
    special_cases = {
        "c++": "c-plus-plus",
        "c#": "c-sharp",
        ".net": "dotnet",
        "f#": "f-sharp",
    }

    if tag_lower in special_cases:
        return special_cases[tag_lower]

    # Convert to lowercase, replace spaces with hyphens
    slug = tag_lower.replace(" ", "-")

    # Remove all non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Replace multiple consecutive hyphens with single hyphen
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug if slug else "tag"


def _normalize_date_for_sorting(d):
    """
    Normalize date/datetime objects for sorting.
    Converts date objects to datetime (at midnight) so they can be compared with datetime objects.
    Returns a comparable value (datetime or empty string for None).
    """
    if d is None:
        return ""
    if isinstance(d, datetime):
        return d
    if isinstance(d, date):
        # Convert date to datetime at midnight for comparison
        return datetime.combine(d, datetime.min.time())
    return ""


class BlogGenerator:
    """Generates a static blog from markdown files."""

    def __init__(self, config: Config):
        """
        Initialize the generator.

        Args:
            config: Blog configuration.
        """
        self.config = config
        self.parser = MarkdownParser()
        self.html_parser = HtmlPageParser()

        # Set up Jinja2 environment with template override support
        loaders = []

        # Priority 1: User custom templates (if directory exists)
        user_template_dir = config.source_dir / "templates"
        if user_template_dir.exists():
            loaders.append(FileSystemLoader(user_template_dir))
            print(f"Found custom templates in {user_template_dir}")

        # Priority 2: Package default templates
        try:
            loaders.append(PackageLoader("ghmd", "templates"))
        except (ValueError, ModuleNotFoundError):
            # Fallback for development
            template_dir = Path(__file__).parent / "templates"
            loaders.append(FileSystemLoader(template_dir))

        self.jinja_env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Add config to global template context
        self.jinja_env.globals["config"] = config

        # Add custom filters
        self.jinja_env.filters["slugify"] = _slugify_tag

    def build(self, output_dir: Optional[Path] = None) -> dict:
        """
        Build the static site.

        Args:
            output_dir: Output directory. Uses config.output_dir if not specified.

        Returns:
            Dictionary with build statistics:
            - md_posts: Number of markdown posts converted to HTML
            - html_pages: Number of HTML pages included
            - total_pages: Total number of pages in the blog
            - posts: List of Post objects (for backward compatibility)
        """
        output = Path(output_dir) if output_dir else self.config.output_dir
        source = self.config.source_dir

        # Clean output directory
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True)

        # Find all markdown files
        md_files = list(source.glob("**/*.md"))

        # Parse all posts
        posts: list[Post] = []
        for md_file in md_files:
            # Skip config file
            if md_file.name == "ghmd.config.yml":
                continue

            # Skip tag description files
            if md_file.parent.name == "tags":
                continue

            post = self.parser.parse_file(md_file, source)

            # Skip drafts
            if post.draft:
                continue

            posts.append(post)

        # Create filtered list for index (exclude static pages)
        index_posts = [post for post in posts if not post.exclude_from_index]

        # Find all HTML files
        html_files = list(source.glob("**/*.html"))

        # Parse all HTML pages
        html_pages: list[HtmlPage] = []
        for html_file in html_files:
            html_page = self.html_parser.parse_file(html_file, source)
            html_pages.append(html_page)

        # Combine posts and HTML pages (only index_posts, not all posts)
        all_items: list[Union[Post, HtmlPage]] = index_posts + html_pages

        # Sort all items (posts and HTML pages) based on config
        # Note: Post objects use date, HtmlPage objects use datetime
        # We normalize both to datetime for accurate comparison
        if self.config.sort_by_update:
            # Sort by update date (fall back to date if update is None), newest first
            # HtmlPage doesn't have update field, so use getattr with fallback
            all_items.sort(
                key=lambda item: (
                    (getattr(item, 'update', None) or item.date) is not None,
                    _normalize_date_for_sorting(getattr(item, 'update', None) or item.date)
                ),
                reverse=True,
            )
        else:
            # Sort by date (newest first), items without dates go last
            all_items.sort(
                key=lambda item: (item.date is not None, _normalize_date_for_sorting(item.date)),
                reverse=True,
            )

        # Generate post pages (ALL markdown posts, including excluded ones)
        for post in posts:
            self._generate_post(post, output)

        # Generate index page with all items (posts and HTML pages)
        self._generate_index(all_items, output)

        # Generate tag indices (only if tags_as_link is enabled)
        tag_count = 0
        if self.config.tags_as_link:
            tag_count = self._generate_tag_indices(all_items, output)

        # Copy assets
        self._copy_assets(output)

        # Copy images from source
        self._copy_images(source, output)

        return {
            "md_posts": len(posts),
            "html_pages": len(html_pages),
            "total_pages": len(all_items),
            "posts": posts,  # For backward compatibility
            "tags": tag_count,
        }

    def _generate_post(self, post: Post, output_dir: Path) -> None:
        """Generate HTML for a single post."""
        # Select template based on post.template field
        template_name = f"{post.template}.html.jinja"
        try:
            template = self.jinja_env.get_template(template_name)
        except:
            # Fall back to post template if not found
            print(f"Warning: Template '{template_name}' not found, using 'post.html.jinja'")
            template = self.jinja_env.get_template("post.html.jinja")

        # Determine if TOC should be shown
        show_toc = self.parser.should_show_toc(
            post, self.config.show_toc, self.config.toc_min_headings
        )

        # Generate custom TOC HTML if needed
        toc_html = ""
        if show_toc:
            toc_html = generate_toc_html(post.headings)

        # Calculate page depth based on output path
        # Count directory separators to determine depth
        depth = str(post.output_path).count('/') if '/' in str(post.output_path) else 0

        # Render template
        html = template.render(
            post=post,
            show_toc=show_toc,
            toc_html=toc_html,
            page_depth=depth,
        )

        # Write to output
        output_path = output_dir / post.output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def _generate_index(self, posts: list[Union[Post, HtmlPage]], output_dir: Path) -> None:
        """Generate the blog index page(s) with pagination."""
        template = self.jinja_env.get_template("index.html.jinja")

        # Smart optimization: if max_posts_per_index_page is 0, treat as "all posts"
        max_posts = self.config.max_posts_per_index_page
        if max_posts == 0:
            max_posts = len(posts)

        # Calculate total pages
        total_pages = (len(posts) + max_posts - 1) // max_posts if posts else 1

        # Generate each page
        for page_num in range(1, total_pages + 1):
            # Slice posts for this page
            start_idx = (page_num - 1) * max_posts
            end_idx = start_idx + max_posts
            page_posts = posts[start_idx:end_idx]

            # Render template with pagination context
            html = template.render(
                posts=page_posts,
                current_page=page_num,
                total_pages=total_pages,
                filtered_tag=None,
                tag_description_html=None,
                page_depth=0,  # Main index is at root level
            )

            # Write to file (index.html for page 1, index2.html for page 2, etc.)
            if page_num == 1:
                index_path = output_dir / "index.html"
            else:
                index_path = output_dir / f"index{page_num}.html"

            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html)

    def _load_tag_description(self, tag: str) -> Optional[str]:
        """
        Load tag description markdown from source directory and convert to HTML.

        Args:
            tag: Tag name (will be slugified to find file).

        Returns:
            HTML content of tag description, or None if not found.
        """
        import markdown

        tag_slug = _slugify_tag(tag)
        desc_path = self.config.source_dir / "tags" / f"{tag_slug}.md"

        if desc_path.exists():
            try:
                with open(desc_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Convert markdown to HTML using same extensions as posts
                html = markdown.markdown(
                    content,
                    extensions=[
                        "pymdownx.highlight",
                        "pymdownx.superfences",
                        "pymdownx.inlinehilite",
                        "pymdownx.tabbed",
                        "pymdownx.tasklist",
                        "tables",
                        "fenced_code",
                        "codehilite",
                    ],
                )
                return html
            except Exception as e:
                print(f"Warning: Could not read tag description for '{tag}': {e}")

        return None

    def _collect_all_tags(self, posts: list[Union[Post, HtmlPage]]) -> set[str]:
        """
        Collect all unique tags from posts.

        Args:
            posts: List of posts (only markdown posts have tags).

        Returns:
            Set of unique tag names.
        """
        tags = set()
        for post in posts:
            # Only markdown posts have tags (HtmlPage doesn't)
            if hasattr(post, "tags") and post.tags:
                tags.update(post.tags)
        return tags

    def _generate_single_tag_index(
        self,
        tag: str,
        posts: list[Union[Post, HtmlPage]],
        output_dir: Path,
    ) -> None:
        """
        Generate index page(s) for a single tag.

        Args:
            tag: Tag name to filter by.
            posts: List of all posts (will be filtered by tag).
            output_dir: Output directory.
        """
        # Filter posts by tag
        tag_posts = [
            post
            for post in posts
            if hasattr(post, "tags") and tag in post.tags
        ]

        # Skip if no posts have this tag
        if not tag_posts:
            return

        # Load tag description (only for first page)
        tag_description_html = self._load_tag_description(tag)

        # Get template
        template = self.jinja_env.get_template("index.html.jinja")

        # Calculate pagination
        max_posts = self.config.max_posts_per_index_page
        if max_posts == 0:
            max_posts = len(tag_posts)

        total_pages = (
            (len(tag_posts) + max_posts - 1) // max_posts if tag_posts else 1
        )

        # Create tag output directory
        tag_slug = _slugify_tag(tag)
        tag_dir = output_dir / "tags" / tag_slug
        tag_dir.mkdir(parents=True, exist_ok=True)

        # Generate each page
        for page_num in range(1, total_pages + 1):
            # Slice posts for this page
            start_idx = (page_num - 1) * max_posts
            end_idx = start_idx + max_posts
            page_posts = tag_posts[start_idx:end_idx]

            # Render template with tag context
            # Tag pages are 2 levels deep (/tags/tutorial/), so need depth=2
            html = template.render(
                posts=page_posts,
                current_page=page_num,
                total_pages=total_pages,
                filtered_tag=tag,
                tag_description_html=tag_description_html if page_num == 1 else None,
                page_depth=2,  # Tag pages are at /tags/{tag}/index.html
            )

            # Write to file
            if page_num == 1:
                index_path = tag_dir / "index.html"
            else:
                index_path = tag_dir / f"index{page_num}.html"

            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html)

    def _generate_tag_indices(
        self, posts: list[Union[Post, HtmlPage]], output_dir: Path
    ) -> int:
        """
        Generate index pages for all tags.

        Args:
            posts: List of all posts.
            output_dir: Output directory.

        Returns:
            Number of tags processed.
        """
        # Collect all unique tags
        tags = self._collect_all_tags(posts)

        # Generate index for each tag
        for tag in sorted(tags):
            self._generate_single_tag_index(tag, posts, output_dir)

        return len(tags)

    def _copy_assets(self, output_dir: Path) -> None:
        """Copy CSS and other static assets to output."""
        assets_src = Path(__file__).parent / "assets"
        assets_dst = output_dir / "assets"

        if assets_src.exists():
            shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
        else:
            raise FileNotFoundError(
                f"Assets directory not found at {assets_src}. "
                "Ensure the package was installed correctly with assets included."
            )

    def _copy_images(self, source_dir: Path, output_dir: Path) -> None:
        """Copy all non-markdown files from source to output, preserving directory structure."""
        for src_file in source_dir.glob("**/*"):
            # Skip if not a file
            if not src_file.is_file():
                continue

            # Skip markdown files (they get converted to HTML)
            if src_file.suffix.lower() == ".md":
                continue

            # Skip config file
            if src_file.name == "ghmd.config.yml":
                continue

            # Copy all other files as-is
            relative = src_file.relative_to(source_dir)
            dst_file = output_dir / relative
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
