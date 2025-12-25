"""
Command-line interface for ghmd-blog.
"""

from pathlib import Path
from typing import Optional

import click

from .config import Config
from .generator import BlogGenerator


@click.group()
@click.version_option()
def main():
    """ghmd-blog: A static blog generator for GitHub markdown repositories."""
    pass


@main.command()
@click.option(
    "--source", "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default="blog",
    help="Source directory containing markdown files (default: blog)",
)
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default="output",
    help="Output directory for generated HTML (default: output)",
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to config file (default: <source>/ghmd.config.yml)",
)
@click.option(
    "--base-url", "-b",
    type=str,
    default=None,
    help="Override base_url from config (e.g., '/' for local, '/blog' for deployment)",
)
def build(source: Path, output: Path, config: Optional[Path], base_url: Optional[str]):
    """Build the static blog from markdown files."""
    click.echo(f"Building blog from {source}...")

    # Load configuration
    cfg = Config.load(config_path=config, source_dir=source)
    cfg.output_dir = output

    # Override base_url if provided
    if base_url is not None:
        cfg.base_url = base_url
        click.echo(f"Using base_url: {base_url}")
    
    # Create generator and build
    generator = BlogGenerator(cfg)
    stats = generator.build(output)

    # Display detailed statistics
    md_count = stats["md_posts"]
    html_count = stats["html_pages"]
    total_count = stats["total_pages"]
    tag_count = stats.get("tags", 0)

    if html_count > 0:
        click.echo(f"✓ Generated {md_count} posts from Markdown + {html_count} HTML pages = {total_count} total pages")
    else:
        click.echo(f"✓ Generated {total_count} posts")

    if tag_count > 0:
        click.echo(f"✓ Created indices for {tag_count} unique tags")

    click.echo(f"✓ Output written to {output}")


@main.command()
@click.option(
    "--source", "-s",
    type=click.Path(file_okay=False, path_type=Path),
    default="blog",
    help="Directory to initialize (default: blog)",
)
def init(source: Path):
    """Initialize a new blog with example files."""
    source = Path(source)
    source.mkdir(parents=True, exist_ok=True)
    
    # Create example config
    config_path = source / "ghmd.config.yml"
    if not config_path.exists():
        config_content = '''# Blog metadata
title: "My Blog"
description: "Welcome to my blog"
author: "Your Name"

# Appearance
theme: "default"
font: "system"

# Features
show_toc: true
toc_min_headings: 3
show_date: true
show_reading_time: true

# Output settings
base_url: "/"
'''
        config_path.write_text(config_content)
        click.echo(f"✓ Created {config_path}")
    
    # Create example post
    post_path = source / "hello-world.md"
    if not post_path.exists():
        post_content = '''---
title: Hello World
date: 2025-01-01
description: My first blog post using ghmd-blog
---

# Welcome to my blog!

This is my **first post** using ghmd-blog.

## Getting Started

Edit this file or create new `.md` files in the `blog` folder.

## Features

- Write in Markdown
- Automatic syntax highlighting
- Table of contents generation
- Clean, responsive design

## Code Example

```python
def hello():
    print("Hello from ghmd-blog!")
```

Happy blogging! 🚀
'''
        post_path.write_text(post_content)
        click.echo(f"✓ Created {post_path}")
    
    click.echo(f"\n✓ Blog initialized in {source}")
    click.echo(f"  Run 'ghmd build -s {source}' to generate your site")


if __name__ == "__main__":
    main()
