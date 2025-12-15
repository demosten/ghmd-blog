"""
Configuration loading and management for ghmd-blog.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml

# Available font options
AVAILABLE_BODY_FONTS = [
    "system",
    "inter",
    "manrope",
    "space-grotesk",
    "outfit",
    "geist",
]

AVAILABLE_CODE_FONTS = [
    "system",
    "jetbrains-mono",
    "fira-code",
    "geist-mono",
]


@dataclass
class Config:
    """Blog configuration with sensible defaults."""

    # Blog metadata
    title: str = "My Blog"
    description: str = ""
    author: str = ""

    # Appearance
    theme_light: str = "default_light"
    theme_dark: str = "default_dark"
    font_body: str = "system"
    font_code: str = "system"

    # Features
    show_toc: bool = True
    toc_min_headings: int = 3
    show_date: bool = True
    show_reading_time: bool = True
    sort_by_update: bool = False
    max_posts_per_index_page: int = 0

    # Output settings
    base_url: str = "/"

    # Internal (not from config file)
    source_dir: Path = field(default_factory=lambda: Path("blog"))
    output_dir: Path = field(default_factory=lambda: Path("output"))

    @classmethod
    def load(cls, config_path: Optional[Path] = None, source_dir: Optional[Path] = None) -> "Config":
        """
        Load configuration from a YAML file.

        Args:
            config_path: Path to config file. If None, looks for ghmd.config.yml in source_dir.
            source_dir: Source directory containing blog posts.

        Returns:
            Config instance with loaded values or defaults.
        """
        config_data = {}

        # Determine source directory
        if source_dir:
            src = Path(source_dir)
        else:
            src = Path("blog")

        # Find config file
        if config_path:
            cfg_path = Path(config_path)
        else:
            cfg_path = src / "ghmd.config.yml"

        # Load config if it exists
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    config_data = loaded

        # Handle backward compatibility: migrate old 'font' to 'font_body'
        if "font" in config_data and "font_body" not in config_data:
            config_data["font_body"] = config_data["font"]

        # Validate body font
        font_body = config_data.get("font_body", cls.font_body)
        if font_body not in AVAILABLE_BODY_FONTS:
            print(f"Warning: Unknown body font '{font_body}'. Available: {', '.join(AVAILABLE_BODY_FONTS)}")
            print(f"Falling back to 'system' font for body text.")
            font_body = "system"

        # Validate code font
        font_code = config_data.get("font_code", cls.font_code)
        if font_code not in AVAILABLE_CODE_FONTS:
            print(f"Warning: Unknown code font '{font_code}'. Available: {', '.join(AVAILABLE_CODE_FONTS)}")
            print(f"Falling back to 'system' font for code blocks.")
            font_code = "system"

        # Build config instance
        config = cls(
            title=config_data.get("title", cls.title),
            description=config_data.get("description", cls.description),
            author=config_data.get("author", cls.author),
            theme_light=config_data.get("theme_light", cls.theme_light),
            theme_dark=config_data.get("theme_dark", cls.theme_dark),
            font_body=font_body,
            font_code=font_code,
            show_toc=config_data.get("show_toc", cls.show_toc),
            toc_min_headings=config_data.get("toc_min_headings", cls.toc_min_headings),
            show_date=config_data.get("show_date", cls.show_date),
            show_reading_time=config_data.get("show_reading_time", cls.show_reading_time),
            sort_by_update=config_data.get("sort_by_update", cls.sort_by_update),
            max_posts_per_index_page=config_data.get("max_posts_per_index_page", cls.max_posts_per_index_page),
            base_url=config_data.get("base_url", cls.base_url),
            source_dir=src,
        )

        return config

    def get_asset_url(self, path: str, depth: int = 0) -> str:
        """
        Get full URL for an asset, respecting base_url and page depth.

        Args:
            path: Asset path (e.g., "assets/css/base.css")
            depth: Number of directory levels deep from root (0 for root, 2 for /tags/tutorial/)

        Returns:
            Properly formatted asset URL
        """
        base = self.base_url.rstrip("/")
        path = path.lstrip("/")

        # If base_url is just "/", use relative paths for local file:// viewing
        # For nested pages, we need to go up the directory tree
        if base == "" or base == "/":
            if depth > 0:
                prefix = "../" * depth
                return f"{prefix}{path}"
            return path

        return f"{base}/{path}"
