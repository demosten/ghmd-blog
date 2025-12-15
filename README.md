# ghmd-blog

A static blog generator that reads markdown from a GitHub repository and deploys to shared hosting.

This project is strongly inspired by [plok.sh](https://www.plok.sh/). I recommend using plok.sh unless you need to self-host your blog (as I do). This is a complete rewrite in Python.

## Features

- 📝 Write posts in Markdown with YAML frontmatter
- 🌐 Include standalone HTML pages alongside markdown posts
- 🔒 Works with private GitHub repositories
- 📤 Deploy to shared hosting via SFTP
- 🎨 17 professionally designed themes (Catppuccin, Rose Pine, Dracula, Tokyo Night, Nord, Gruvbox, GitHub)
- 🌈 Mix and match any light theme with any dark theme
- 🌓 Manual light/dark theme toggle with automatic system preference detection
- 🔤 10 carefully selected free fonts with separate body/code configuration (6 body fonts + 4 code fonts)
- 🏷️ Tag filtering with dedicated index pages and optional tag descriptions
- 📑 Auto-generated table of contents
- ✨ Syntax highlighting for code blocks (with theme-aware colors)
- 📄 Index pagination with configurable posts per page
- 🚀 GitHub Actions for automatic deployment
- 🔗 Relative paths for local viewing (open output HTML files directly in browser)
- 📁 Automatic copying of all static files (images, PDFs, JSON, etc.)
- 💾 Theme preference persists across all pages (works with both local files and HTTP serving)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/demosten/ghmd-blog.git
cd ghmd-blog

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Initialize a New Blog

```bash
ghmd init --source ./blog
```

This creates a `blog` folder with an example configuration and post.

### Build Your Blog

```bash
ghmd build --source ./blog --output ./output
```

### Project Structure

```
your-repo/
├── blog/
│   ├── ghmd.config.yml    # Configuration (optional)
│   ├── hello-world.md     # Your posts
│   ├── tags/              # Tag descriptions (optional)
│   │   ├── python.md      # Description for "python" tag
│   │   └── tutorial.md    # Description for "tutorial" tag
│   ├── images/            # Static files (all non-.md files copied to output)
│   └── data.json          # Any file type is preserved as-is
└── .github/
    └── workflows/
        └── deploy.yml     # GitHub Action for deployment
```

## Configuration

Create `blog/ghmd.config.yml`:

```yaml
# Blog metadata
title: "My Blog"
description: "Thoughts on code and life"
author: "Your Name"

# Appearance
theme_light: "default_light"  # Light theme (see Available Themes below)
theme_dark: "default_dark"    # Dark theme (see Available Themes below)
font_body: "system"           # Body font (see Available Fonts below)
font_code: "system"           # Code font (see Available Fonts below)

# Features
show_toc: true                  # Show table of contents
toc_min_headings: 3             # Minimum headings to show TOC
show_date: true                 # Show post dates
show_reading_time: true         # Show estimated reading time
sort_by_update: false           # Sort posts by update date (false = sort by original date)
max_posts_per_index_page: 0     # Posts per index page (0 = all posts on one page)
tags_as_link: true              # Enable tag links in index pages (creates /tags/ folder structure)

# Output settings
base_url: "/"                   # Base URL for links
```

### Available Themes

The blog now supports multiple color themes for both light and dark modes. You can mix and match different themes for light and dark modes.

**Light Themes:**

- `default_light` - Clean, modern light theme (default)
- `github_light` - GitHub-inspired light theme
- `catppuccin_latte_light` - Catppuccin Latte (warm, pastel light theme)
- `rose_pine_dawn_light` - Rosé Pine Dawn (soft, warm light theme)
- `gruvbox_light` - Gruvbox Light (retro groove light theme)

**Dark Themes:**

- `default_dark` - Clean, modern dark theme (default)
- `github_dark` - GitHub-inspired dark theme
- `catppuccin_mocha_dark` - Catppuccin Mocha (original, darkest variant)
- `catppuccin_frappe_dark` - Catppuccin Frappé (muted, subdued dark theme)
- `catppuccin_macchiato_dark` - Catppuccin Macchiato (medium contrast dark theme)
- `rose_pine_dark` - Rosé Pine (main variant, warm dark theme)
- `rose_pine_moon_dark` - Rosé Pine Moon (alternative dark variant)
- `dracula_dark` - Dracula (vibrant, popular dark theme)
- `tokyo_night_dark` - Tokyo Night (cool, blue-tinted dark theme)
- `nord_dark` - Nord (arctic, north-bluish dark theme)
- `gruvbox_dark` - Gruvbox Dark (retro groove dark theme)

**Example configurations:**

```yaml
# Use different themes for light and dark modes
theme_light: "github_light"
theme_dark: "tokyo_night_dark"

# Or match theme families
theme_light: "catppuccin_latte_light"
theme_dark: "catppuccin_mocha_dark"

# Classic defaults
theme_light: "default_light"
theme_dark: "default_dark"
```

### Available Fonts

The blog supports separate font configuration for body text and code blocks, giving you full control over typography:

**Body Fonts (`font_body`) - For body text:**

- `system` - Native system fonts (default, no web font loading)
- `inter` - Clean, modern sans-serif with excellent readability
- `manrope` - Geometric sans-serif with a friendly feel
- `space-grotesk` - Unique geometric sans-serif with character
- `outfit` - Rounded geometric sans-serif
- `geist` - Vercel's modern sans-serif font

**Code Fonts (`font_code`) - For code blocks:**

- `system` - Native monospace fonts (default)
- `jetbrains-mono` - Developer-focused monospace from JetBrains
- `fira-code` - Monospace with programming ligatures
- `geist-mono` - Vercel's modern monospace font

**Notes:**

- Configure body and code fonts independently for full customization
- All fonts except `system` are loaded from CDNs (Google Fonts or jsDelivr)
- The `system` option uses native fonts for maximum performance (no web font loading)
- Mix and match any combination (e.g., Inter for text + Fira Code for code)

**Examples:**

```yaml
# Modern web fonts for both text and code
font_body: "inter"
font_code: "fira-code"

# Mix modern body text with developer-focused code font
font_body: "geist"
font_code: "jetbrains-mono"

# Maximum performance with system fonts
font_body: "system"
font_code: "system"

# Unique typography with Space Grotesk
font_body: "space-grotesk"
font_code: "geist-mono"
```

## Tag Filtering

The blog supports automatic tag filtering with dedicated index pages for each tag. When enabled (`tags_as_link: true`), tags become clickable in the main index, leading to filtered views showing only posts with that tag.

### Configuration

```yaml
tags_as_link: true  # Enable tag links (default: true)
```

- Set to `true` (default): Tags are clickable links, and `/tags/` folder structure is created
- Set to `false`: Tags are displayed as plain text, no tag filtering pages are generated

### How It Works

1. **Add tags to posts** in frontmatter:
   ```yaml
   ---
   title: My Post
   tags: [python, tutorial, web]
   ---
   ```

2. **Tags become clickable** in the main index page, leading to tag-specific index pages

3. **(Optional) Add tag descriptions** by creating Markdown files in `blog/tags/`:
   ```bash
   blog/tags/python.md      # Description for the "python" tag
   blog/tags/tutorial.md    # Description for the "tutorial" tag
   ```

### Tag Description Files

Tag description files are simple Markdown files (no frontmatter needed) that appear at the top of tag index pages:

**Example: `blog/tags/python.md`**
```markdown
**Python** is a high-level programming language known for its simplicity and versatility. These posts explore Python programming, from basics to advanced topics.
```

**Notes:**
- Tag description files are converted from Markdown to HTML
- They appear only on the first page of paginated tag indices
- Tag `.md` files are automatically excluded from the main blog index
- Tag names are slugified for URLs (e.g., "C++" becomes "c-plus-plus", "Machine Learning" becomes "machine-learning")

### URL Structure

```
Main index:       /index.html
Tag "python":     /tags/python/index.html
Tag "tutorial":   /tags/tutorial/index.html, /tags/tutorial/index2.html (if paginated)
```

### Features

- **Optional tag linking**: Enable or disable tag filtering with `tags_as_link` config option
- **Server-side filtering**: Each tag gets its own static index pages (no JavaScript required)
- **Pagination support**: Tag indices respect the `max_posts_per_index_page` setting
- **Smart tag slugification**: Handles special characters ("C++", "C#", spaces, etc.)
- **Tag descriptions**: Optional Markdown files provide context for each tag
- **Clickable only in main index**: Tags in tag-filtered views are displayed as plain text (not links)

## Pagination

The blog supports index page pagination to split long post lists across multiple pages:

### Configuration

```yaml
max_posts_per_index_page: 10  # Show 10 posts per page
```

- Set to `0` (default): All posts appear on a single index page
- Set to any positive integer: Posts are split across multiple pages (`index.html`, `index2.html`, `index3.html`, etc.)

### Features

- **Automatic page splitting**: Posts are distributed across pages based on your configured limit
- **Page navigation**: Numbered links appear at the bottom of each index page (e.g., "1 2 3 4")
- **Current page highlighting**: The active page number is styled differently and not clickable
- **Smart optimization**: When set to 0 or when total posts ≤ limit, only one page is created with no pagination UI
- **Back button navigation**: Post pages use browser history to return users to the exact index page they came from

### Examples

```yaml
# Default: all posts on one page
max_posts_per_index_page: 0

# Show 5 posts per page
max_posts_per_index_page: 5

# Show 20 posts per page
max_posts_per_index_page: 20
```

## Static Files

The generator automatically copies **all non-markdown files** from your source directory to the output, preserving the directory structure. This includes:

- Images (`.jpg`, `.png`, `.gif`, `.webp`, `.svg`, etc.)
- Videos, PDFs, JSON files, text files
- Any other static assets

Files are excluded from copying:

- `.md` files (converted to HTML)
- `ghmd.config.yml` (configuration file)

This means you can organize your blog with images, downloads, and other assets alongside your markdown posts.

## Theme System

The blog includes 17 professionally designed themes with a manual light/dark toggle:

### Features

- **17 themes** from popular color schemes (Catppuccin, Rose Pine, Dracula, Tokyo Night, Nord, Gruvbox, GitHub)
- **Mix and match** — choose different themes for light and dark modes
- **Toggle button** in the header (top-right) to switch between light and dark themes
- **System preference detection** — automatically uses your OS theme preference on first visit
- **Manual override** — click the toggle to set your preferred theme
- **Persistent across pages** — theme choice is preserved when navigating between posts
- **Works everywhere** — functions correctly whether viewing local files or serving via HTTP

### How It Works

1. On first visit with no saved preference, the blog matches your system's light/dark mode
2. Click the theme toggle (🌙/☀️) to switch themes
3. Your preference is saved and persists across all pages
4. Theme applies to all content including syntax highlighting in code blocks

### Technical Details

- **Local files** (`file://` protocol): Uses URL parameters to pass theme between pages
- **HTTP serving**: Uses localStorage for theme persistence
- **Fallback**: System preference via `prefers-color-scheme` media query

## Writing Posts

Create `.md` files in your `blog` folder:

```markdown
---
title: My First Post
date: 2025-01-15
update: 2025-01-16
description: A brief summary for previews
author: "Your Name"
tags: [intro, tutorial]
draft: false
toc: true
---

# Welcome!

Your content here...
```

### Frontmatter Options

| Field         | Description                           | Required           |
| ------------- | ------------------------------------- | ------------------ |
| `title`       | Post title                            | No (uses filename) |
| `date`        | Publication date (YYYY-MM-DD)         | No                 |
| `update`      | Last updated date (YYYY-MM-DD)        | No                 |
| `description` | Short summary                         | No                 |
| `author`      | Post author (overrides config author) | No                 |
| `tags`        | List of tags                          | No                 |
| `draft`       | Set to `true` to exclude from build   | No                 |
| `toc`         | Override global TOC setting           | No                 |

**Author field behavior:**

- If `author` is set in frontmatter, it will be displayed for that post
- If not set in frontmatter, falls back to the global `author` from config
- If neither is set, no author is displayed
- Displayed as "By {author}" under the post title (not shown on index pages)
- Supports multiple authors as a comma-separated string (e.g., `author: "Jane Doe, John Smith"`)

## HTML Pages

In addition to Markdown posts, you can include standalone HTML pages in your blog. These pages appear in the blog index alongside your markdown posts but are not converted or modified during the build process.

### How It Works

1. **Add HTML files** to your blog source directory (e.g., `blog/my-page.html`)
2. **Metadata extraction**: The generator automatically extracts metadata from HTML tags:
   - **Title**: Extracted from `<title>` tag (falls back to filename if not found)
   - **Description**: Extracted from `<meta name="description">` tag (optional)
   - **Date**: Uses file modification timestamp (full datetime including time-of-day)
3. **Automatic inclusion**: HTML pages appear in the blog index sorted by timestamp alongside markdown posts
4. **Direct copying**: HTML files are copied as-is to the output directory (no conversion or modification)

**Note on sorting**: HTML pages use the full file modification timestamp (including hours/minutes/seconds), so multiple HTML files modified on the same day will sort by their exact modification time. Markdown posts use only the date from frontmatter (treated as midnight), so HTML pages modified later on the same day will appear before markdown posts with that date.

### Use Cases

- **Custom landing pages**: Create styled pages with custom HTML/CSS/JavaScript
- **Interactive demos**: Embed JavaScript applications or visualizations
- **External content**: Include pre-built HTML from other tools
- **Special layouts**: Design pages that don't fit the standard blog post template

### Example HTML Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Custom Page</title>
    <meta name="description" content="A custom HTML page in my blog">
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; }
    </style>
</head>
<body>
    <h1>My Custom Page</h1>
    <p>This is a standalone HTML page that appears in the blog index.</p>
</body>
</html>
```

### Build Output

When you build your blog, the output shows a breakdown of generated pages:

```bash
$ ghmd build --source ./blog --output ./output
Building blog from blog...
✓ Generated 3 posts from Markdown + 2 HTML pages = 5 total pages
✓ Created indices for 4 unique tags
✓ Output written to output
```

This helps you track both converted markdown posts and included HTML pages.

## Deployment

### GitHub Actions + SFTP

1. Add these secrets to your GitHub repository:
   
   - `SFTP_HOST` — Your hosting server
   - `SFTP_PORT` — SFTP port (usually 22)
   - `SFTP_USER` — SFTP username
   - `SFTP_PASSWORD` — SFTP password
   - `SFTP_REMOTE_PATH` — Destination path (e.g., `/public_html/`)

2. Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Blog

on:
  push:
    paths:
      - 'blog/**'
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ghmd-blog
        run: pip install ./ghmd-blog  # or from PyPI when published

      - name: Build blog
        run: ghmd build --source ./blog --output ./output

      - name: Deploy via SFTP
        uses: wlixcc/SFTP-Deploy-Action@v1.2.4
        with:
          server: ${{ secrets.SFTP_HOST }}
          port: ${{ secrets.SFTP_PORT }}
          username: ${{ secrets.SFTP_USER }}
          password: ${{ secrets.SFTP_PASSWORD }}
          local_path: ./output/*
          remote_path: ${{ secrets.SFTP_REMOTE_PATH }}
          sftp_only: true
```

3. Push to your repository — the blog deploys automatically!

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black ghmd/
ruff check ghmd/
```

The `example/blog/` directory is tracked to provide reference content for testing.

```bash
source .venv/bin/activate
python -m ghmd.cli build --source ./example/blog --output ./example/output
```

Then you can load open `./example/output/index.html` in your browser to see the 
output locally.

## License

MIT License — see [LICENSE](LICENSE) for details.
