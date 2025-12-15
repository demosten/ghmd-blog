# CLAUDE.md - Development Context for ghmd-blog

This file provides context for AI assistants (like Claude Code) to help continue development of this project.

## Project Overview

**ghmd-blog** is a static blog generator that:
- Reads markdown files from a `/blog` directory
- Parses YAML frontmatter for metadata
- Generates static HTML files
- Deploys to shared hosting via SFTP (using GitHub Actions)

**Key differentiators from similar tools (like plok.sh):**
- Works with **private** GitHub repositories
- Self-hosted on **shared hosting** (no vendor lock-in)
- Pure Python implementation

## Documentation Structure

The project documentation is split into multiple files:

- **README.md** - Brief project overview with quick start guide (for end users browsing the repository)
- **MANUAL.md** - Comprehensive user documentation covering all configuration options, features, deployment, and development
- **CLAUDE.md** - Development context and implementation details (this file, for AI assistants and developers)

When users need detailed information about any feature, configuration, or usage, refer them to MANUAL.md.

### Installation Approaches

The project supports two installation methods:

1. **Install as package**: `pip install -e .` - Creates the `ghmd` command
2. **Install dependencies only**: `pip install -r requirements.txt` - Use `python -m ghmd.cli` instead

Both approaches are documented in README.md and MANUAL.md. The `python -m ghmd.cli` approach works because Python runs the module directly from source when all dependencies are installed.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRIVATE GITHUB REPO                             │
│  /blog/*.md  ──────────────────────────────────────────────────────│
└─────────────────────────┬───────────────────────────────────────────┘
                          │ git push triggers
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     GITHUB ACTIONS                                  │
│  1. Checkout repo                                                   │
│  2. pip install ghmd-blog                                           │
│  3. ghmd build --source ./blog --output ./output                    │
│  4. SFTP upload ./output/* to shared hosting                        │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ SFTP
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SHARED HOSTING                                  │
│  Static HTML files served directly                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## File Structure

```
ghmd-blog/
├── .gitignore                 # Git ignore patterns
├── ghmd/                      # Main Python package
│   ├── __init__.py            # Package exports
│   ├── cli.py                 # Click CLI (ghmd build, ghmd init)
│   ├── config.py              # Config dataclass + YAML loading
│   ├── parser.py              # Markdown parsing + frontmatter
│   ├── html_parser.py         # HTML page parsing + metadata extraction
│   ├── generator.py           # HTML generation orchestrator
│   ├── toc.py                 # Table of contents generation
│   └── templates/             # Jinja2 templates
│       ├── base.html.jinja    # Base layout
│       ├── index.html.jinja   # Blog listing page (supports tag filtering)
│       └── post.html.jinja    # Individual post page
├── assets/
│   └── css/
│       ├── base.css                    # Shared formatting rules (all themes)
│       ├── fonts/                      # Font CSS files (10 fonts total)
│       │   ├── body/                   # Body fonts (6 fonts)
│       │   │   ├── system.css          # Native system fonts (default)
│       │   │   ├── inter.css           # Inter font from Google Fonts
│       │   │   ├── manrope.css         # Manrope font from Google Fonts
│       │   │   ├── space-grotesk.css   # Space Grotesk from Google Fonts
│       │   │   ├── outfit.css          # Outfit font from Google Fonts
│       │   │   └── geist.css           # Geist font from jsDelivr CDN
│       │   └── code/                   # Code fonts (4 fonts)
│       │       ├── system.css          # Native monospace fonts (default)
│       │       ├── jetbrains-mono.css  # JetBrains Mono from Google Fonts
│       │       ├── fira-code.css       # Fira Code from Google Fonts
│       │       └── geist-mono.css      # Geist Mono from jsDelivr CDN
│       ├── default_light.css           # Default light theme colors
│       ├── default_dark.css            # Default dark theme colors
│       ├── syntax_light.css            # Light mode syntax highlighting
│       ├── syntax_dark.css             # Dark mode syntax highlighting
│       └── [17 additional theme files] # Catppuccin, Rose Pine, Dracula, etc.
├── example/
│   ├── blog/                  # Example blog for testing
│   │   └── tags/              # Example tag descriptions
│   │       ├── python.md      # Tag description example
│   │       └── tutorial.md    # Tag description example
│   └── output/                # Generated output (gitignored)
├── pyproject.toml             # Package configuration
├── requirements.txt           # Dependencies
├── CLAUDE.md                  # Development context (this file)
├── README.md                  # Brief project overview
└── MANUAL.md                  # Comprehensive user documentation
```

## Core Components

### 1. Config (`ghmd/config.py`)
- Dataclass with all configuration options
- `Config.load(config_path, source_dir)` - loads from YAML or uses defaults
- Config file is optional: `ghmd.config.yml` in blog directory
- `get_asset_url(path, depth=0)` - generates URLs respecting base_url and page depth
  - Returns relative paths when base_url is `/` for local viewing
  - Depth parameter handles nested pages (0 for root, 2 for `/tags/tutorial/`)
  - Uses `../` prefixes for nested pages to maintain correct asset paths
- `max_posts_per_index_page` - controls pagination (0 = all posts on one page, >0 = split across multiple pages)
- `tags_as_link` - controls tag linking (True = tags as clickable links with /tags/ folder, False = tags as plain text)
- `AVAILABLE_BODY_FONTS` - list of valid body font options (6 fonts)
- `AVAILABLE_CODE_FONTS` - list of valid code font options (4 fonts)
- Font validation with separate validation for body and code fonts
- Backward compatibility: old `font` field automatically migrates to `font_body`

### 2. Parser (`ghmd/parser.py`)
- `MarkdownParser` class
- `parse_file(file_path, source_dir) -> Post` - parses single markdown file
- `Post` dataclass holds all post data (frontmatter + rendered HTML)
  - Includes optional `update` field for "Last updated" date
  - Includes optional `author` field for post author (overrides config author)
- Uses `python-frontmatter` for YAML extraction
- Uses `markdown` library with `pymdown-extensions` for rendering
- Extracts headings for TOC generation
- TocExtension configured with `permalink=False` (no ¶ symbols)

### 3. HTML Parser (`ghmd/html_parser.py`)
- `HtmlPageParser` class - parses standalone HTML files
- `parse_file(file_path, source_dir) -> HtmlPage` - parses HTML file and extracts metadata
- `HtmlPage` dataclass holds HTML page data (no conversion, just metadata)
  - `title`: Extracted from `<title>` tag (falls back to filename)
  - `description`: Extracted from `<meta name="description">` tag (optional)
  - `date`: Uses file modification time as `datetime` (preserves full timestamp for accurate sorting)
  - `is_html`: Always `True` to distinguish from markdown posts
- `TitleExtractor` class - HTML parser to extract title from `<title>` tag
- HTML files are copied as-is to output (no conversion or template rendering)
- Enables including custom HTML pages alongside markdown posts in the blog index

### 4. Generator (`ghmd/generator.py`)
- `BlogGenerator` class
- `build(output_dir) -> dict` - main entry point, returns build statistics
  - Returns dictionary with: `md_posts`, `html_pages`, `total_pages`, `posts`, `tags`
- Orchestrates: find files → parse markdown/HTML → render templates → generate tag indices → copy assets → copy static files
- Processes both `.md` files (converted to HTML) and `.html` files (copied as-is)
- Skips `.md` files in `tags/` directory (used for tag descriptions, not blog posts)
- Combines markdown posts and HTML pages into unified index
- `_normalize_date_for_sorting()` - helper function to compare `date` (from Post) and `datetime` (from HtmlPage) objects
  - Converts `date` objects to `datetime` at midnight for accurate comparison
  - Ensures HTML pages with modification times on same day sort correctly
- Sorting logic respects `sort_by_update` config:
  - If `false` (default): sorts by `date` field (newest first)
  - If `true`: sorts by `update` field, falls back to `date` if update is None
  - HTML pages sorted by full modification timestamp (preserves time-of-day ordering)
  - Markdown posts sorted by frontmatter date (converted to midnight datetime)
- `_generate_index()` - generates index page(s) with pagination support:
  - When `max_posts_per_index_page = 0`: creates single index.html with all items
  - When `max_posts_per_index_page > 0`: splits items across multiple pages (index.html, index2.html, index3.html, etc.)
  - Smart optimization: treats 0 as "all items" to avoid unnecessary pagination logic
  - Passes `page_depth=0` and `filtered_tag=None` for main index
- `_generate_post()` - renders only markdown posts (not HTML pages)
  - Calculates page depth based on output path for correct asset URLs
- `_copy_images()` - copies ALL non-.md, non-.html files preserving directory structure
  - HTML files are handled separately (copied with metadata extraction)
- **Tag filtering methods** (only run when `tags_as_link` is True):
  - `_slugify_tag(tag)` - converts tag names to URL-safe slugs (handles special characters like "C++", "C#", spaces)
  - `_load_tag_description(tag)` - loads and converts tag description from `source/tags/{slug}.md` to HTML
  - `_collect_all_tags(posts)` - extracts all unique tags from posts
  - `_generate_single_tag_index(tag, posts, output_dir)` - generates paginated index for one tag
  - `_generate_tag_indices(posts, output_dir)` - generates index pages for all tags, returns tag count (skipped if `tags_as_link` is False)
  - Tag pages created at `/tags/{slug}/index.html` with `page_depth=2` for correct asset paths
- Uses Jinja2 for templating markdown posts

### 5. TOC (`ghmd/toc.py`)
- `generate_toc_html(headings)` - creates nested HTML list from headings
- `count_headings(headings)` - for deciding whether to show TOC

### 6. CLI (`ghmd/cli.py`)
- `ghmd build` - build the static site
  - Displays build statistics: markdown posts, HTML pages, tag count, and total count
  - Format: "Generated X posts from Markdown + Y HTML pages = Z total pages"
  - Shows "Created indices for N unique tags" when tags are present
  - Shows simple format when no HTML pages: "Generated X posts"
- `ghmd init` - scaffold a new blog with example files

### 7. Theme System (`base.html.jinja`, `base.css`, theme files)
- **Named themes**: Separate light and dark theme configuration (`theme_light`, `theme_dark`)
- **17 Available themes**:
  - **Light**: default_light, github_light, catppuccin_latte_light, rose_pine_dawn_light, gruvbox_light
  - **Dark**: default_dark, github_dark, catppuccin_mocha_dark, catppuccin_frappe_dark, catppuccin_macchiato_dark, rose_pine_dark, rose_pine_moon_dark, dracula_dark, tokyo_night_dark, nord_dark, gruvbox_dark
- **CSS Architecture**:
  - `base.css`: Shared formatting rules (layout, typography, spacing) used by all themes
  - Theme files: Only contain color variables scoped to `:root[data-theme="light"]` or `:root[data-theme="dark"]`
  - CSS load order: base.css → body_font.css → code_font.css → theme_light.css → theme_dark.css → syntax_light.css → syntax_dark.css
- **Toggle button**: Positioned absolutely in header (top-right)
- **CSS approach**: Uses `data-theme` attribute on `:root` element
  - Light theme: `:root[data-theme="light"]`
  - Dark theme: `:root[data-theme="dark"]`
- **JavaScript flow**:
  1. **Pre-render script** (in `<head>`): Sets theme immediately to prevent flash
  2. **Main script** (at end of `<body>`): Handles toggle button and persistence
- **Persistence strategy**:
  - Priority 1: URL parameter (`?theme=dark`)
  - Priority 2: localStorage (`theme` key)
  - Priority 3: System preference (`prefers-color-scheme`)
- **Cross-page persistence**:
  - `updateAllLinks()`: Adds `?theme=X` to all internal links
  - `updateCurrentUrl()`: Updates current page URL using `history.replaceState()`
- **State management**: `currentTheme` variable tracks active theme in memory

### 8. Font System (`assets/css/fonts/`, `base.html.jinja`)
- **10 Available fonts** with separate configuration for body and code:
  - **Body fonts** (6): system, inter, manrope, space-grotesk, outfit, geist
  - **Code fonts** (4): system, jetbrains-mono, fira-code, geist-mono
- **CSS Architecture**:
  - Fonts organized in `assets/css/fonts/body/` and `assets/css/fonts/code/` directories
  - Body font files only define `--font-sans` CSS variable
  - Code font files only define `--font-mono` CSS variable
  - Theme files contain no font variables (only colors and spacing)
  - Two font CSS files loaded: one for body, one for code
  - CSS load order: base.css → body font → code font → theme files
- **Configuration**:
  - `font_body`: Controls body text font (sans-serif fonts)
  - `font_code`: Controls code block font (monospace fonts)
  - Mix and match any combination (e.g., inter + fira-code)
- **Font sources**:
  - Google Fonts: inter, manrope, space-grotesk, outfit, jetbrains-mono, fira-code
  - jsDelivr CDN: geist, geist-mono (Vercel's fonts)
  - Native system fonts: system (no web font loading)
- **Validation**: Separate validation for body and code fonts with graceful fallback to `system`
- **Backward compatibility**: Old `font` field automatically migrates to `font_body`

### 9. Template Override System (`ghmd/generator.py`, `ghmd/templates/partials/`)
- **Purpose**: Allows users to customize blog appearance without modifying core template files
- **Architecture**: Uses Jinja2's `ChoiceLoader` for priority-based template loading
- **Template Loading Priority**:
  1. **User custom templates**: `blog/templates/` (highest priority)
  2. **Package default templates**: `ghmd/templates/` (fallback)
- **Partial Templates**:
  - `partials/header.html.jinja` - Site header with title, description, theme toggle
  - `partials/footer.html.jinja` - Site footer with copyright and links
  - Extracted from `base.html.jinja` for granular customization
- **Implementation Details**:
  - `ChoiceLoader` configured in `generator.py` `__init__()` (lines 93-113)
  - Checks if `config.source_dir / "templates"` exists before adding to loader stack
  - Prints message when custom templates directory is found
  - Falls back gracefully if custom template missing
- **User Workflow**:
  1. User creates `blog/templates/partials/header.html.jinja` to override header
  2. Generator detects custom template and uses it instead of default
  3. Custom templates committed to user's fork (in `blog/templates/`)
  4. Default templates live in `ghmd/templates/` (tracked separately)
  5. No merge conflicts when pulling upstream updates
- **Full Template Override**:
  - Users can override any template: `base.html.jinja`, `post.html.jinja`, `page.html.jinja`, `index.html.jinja`
  - Responsible for maintaining complete template structure when overriding full templates
  - Partials recommended for most use cases
- **Template Variables Available**:
  - `config` - Global configuration object with all settings
  - `post` / `posts` - Post data (context-dependent)
  - `page_depth` - Directory depth for correct asset URL generation
  - `filtered_tag` / `tag_description_html` - Tag filtering context (index pages)
- **Examples**: See `example/blog/templates/partials/` for working examples

## Data Flow

### Markdown Posts

```
blog/hello-world.md
        │
        ▼
┌───────────────────┐
│  frontmatter.load │  Extract YAML + content
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  markdown.convert │  MD → HTML with extensions
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Post dataclass   │  title, date, content_html, etc.
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Jinja2 render    │  post.html.jinja + Post data
└─────────┬─────────┘
          │
          ▼
output/hello-world.html
```

### HTML Pages

```
blog/my-page.html
        │
        ▼
┌───────────────────┐
│  HTMLParser       │  Extract <title> and <meta> tags
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  HtmlPage         │  title, date, description
│  dataclass        │  (metadata only, no conversion)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Copy as-is       │  No template rendering
└─────────┬─────────┘
          │
          ▼
output/my-page.html
```

Both markdown posts and HTML pages are combined in the blog index, sorted by date.

## Configuration Options

```yaml
# ghmd.config.yml
title: "Blog Title"           # Site title
description: "Tagline"        # Site description
author: "Name"                # Author name

theme_light: "default_light"  # Light theme (17 themes available)
theme_dark: "default_dark"    # Dark theme (17 themes available)
font_body: "system"           # Body font (6 fonts available)
font_code: "system"           # Code font (4 fonts available)

show_toc: true                # Enable table of contents
toc_min_headings: 3           # Minimum headings to show TOC
show_date: true               # Show post dates
show_reading_time: true       # Show "X min read"
sort_by_update: false         # Sort by update date (false = sort by original date)
max_posts_per_index_page: 0   # Posts per index page (0 = all on one page)
tags_as_link: true            # Enable tag links in index pages (creates /tags/ folder structure)

base_url: "/"                 # Base URL for all links
```

## Post Frontmatter

```yaml
---
title: Post Title             # Required (or uses filename)
date: 2025-01-15              # YYYY-MM-DD format (publication date)
update: 2025-01-16            # YYYY-MM-DD format (last updated date)
description: Summary          # For previews/meta
author: "Author Name"         # Optional, overrides config author
tags: [tag1, tag2]            # Optional tags
draft: true                   # Exclude from build
toc: false                    # Override global show_toc
exclude_from_index: false     # Exclude from blog index (but still generate HTML)
template: "post"              # Template to use: "post" or "page"
---
```

**Static pages:**
- Set `exclude_from_index: true` to exclude a page from the blog index
- Use `template: "page"` to apply the simplified page template (no TOC, reading time, dates, author, or tags)
- Individual HTML pages are still generated and can be linked from footer or other pages
- Useful for: License, Privacy Policy, About, Contact, Terms of Service, etc.
- Both fields default to False and "post" respectively for backward compatibility

**Author field behavior:**
- If `author` is set in frontmatter, it overrides the global config `author`
- If not set, falls back to `config.author`
- If neither exists, no author is displayed
- Displayed as "By {author}" under post title on individual post pages
- NOT displayed on index pages
- Supports multiple authors as comma-separated string (e.g., "Jane Doe, John Smith")

## Dependencies

| Package | Purpose |
|---------|---------|
| `python-frontmatter` | Parse YAML frontmatter |
| `markdown` | Convert MD to HTML |
| `pymdown-extensions` | Extra MD features (tables, code, etc.) |
| `Pygments` | Syntax highlighting |
| `Jinja2` | HTML templating |
| `PyYAML` | Config file parsing |
| `click` | CLI framework |

## Git Configuration

The project includes a `.gitignore` file with comprehensive ignore patterns:

- **Python artifacts**: `__pycache__/`, `*.pyc`, `*.pyo`, `*.egg-info/`
- **Build artifacts**: `dist/`, `build/`, `*.egg`
- **Virtual environments**: `venv/`, `env/`, `.venv/`
- **IDE files**: `.vscode/`, `.idea/`, `*.swp`
- **OS files**: `.DS_Store`, `Thumbs.db`
- **Testing**: `.pytest_cache/`, `.coverage`, `htmlcov/`
- **Generated output**: `example/output/` (since it's regenerated by `ghmd build`)

User blog directories are NOT ignored by default, allowing developers to commit example content.

## Development Commands

### Installation Options

**Option 1: Install as package (recommended)**
```bash
# Install in dev mode (makes 'ghmd' command available)
pip install -e .

# Or with dev dependencies (pytest, black, ruff)
pip install -e ".[dev]"
```

**Option 2: Install dependencies only**
```bash
# Install only runtime dependencies
pip install -r requirements.txt

# Use 'python -m ghmd.cli' instead of 'ghmd' for all commands
```

### Command Usage

```bash
# Build example blog
ghmd build --source ./example/blog --output ./example/output
# Or: python -m ghmd.cli build --source ./example/blog --output ./example/output

# Initialize new blog
ghmd init --source ./myblog
# Or: python -m ghmd.cli init --source ./myblog

# Run with short options
ghmd build -s ./blog -o ./output
# Or: python -m ghmd.cli build -s ./blog -o ./output
```

## Implementation Status

### Phase 1 (MVP) - ✅ COMPLETE
- [x] Project structure
- [x] Config loading
- [x] Markdown + frontmatter parsing
- [x] HTML generation
- [x] Index page
- [x] CLI (build, init)
- [x] Default theme + dark mode
- [x] Manual light/dark theme toggle with persistence
- [x] System preference detection for themes
- [x] Syntax highlighting (theme-aware)
- [x] Table of contents
- [x] Reading time
- [x] Relative path support for local viewing
- [x] Static file copying (all non-.md files)

### Phase 2 (Features) - ✅ COMPLETE
- [x] Multiple themes (17 themes: Catppuccin, Rose Pine, Dracula, Tokyo Night, Nord, Gruvbox, GitHub)
- [x] Named theme system (separate light/dark theme selection)
- [x] Font options (10 fonts with separate body/code configuration: 6 body + 4 code fonts)
- [x] Index pagination (configurable posts per page)
- [x] Author field (config + frontmatter with fallback logic)
- [x] HTML page support (standalone HTML files in blog index)
- [x] Build statistics (detailed markdown/HTML page counts)
- [x] Static pages (exclude_from_index + template selection)
- [x] Tag filtering (server-side with dedicated index pages and optional descriptions)

### Phase 3 (Deployment) - TODO
- [ ] GitHub Actions workflow template
- [ ] SFTP deployment documentation
- [ ] SSH key authentication option

### Phase 4 (Enhancements) - FUTURE
- [ ] RSS feed generation
- [ ] Sitemap.xml generation
- [ ] Custom analytics integration
- [ ] Client-side search
- [ ] `ghmd serve` local dev server with hot reload
- [ ] Links page (like Linktree)
- [ ] Subdirectory/nested posts in TOC
- [ ] Image optimization
- [ ] Draft preview mode

## Known Issues / Tech Debt

1. **Duplicate meta description** - `base.html.jinja` and `post.html.jinja` both emit description meta tag
2. **No error handling** - Parser doesn't gracefully handle malformed frontmatter
3. **No tests** - Need pytest test suite

## Implementation Notes

Key implementation details that may not be obvious from the architecture overview:

1. **Date/DateTime Handling** - The codebase uses both `date` and `datetime` types intentionally:
   - Markdown posts use `date` objects (from frontmatter YAML parsing)
   - HTML pages use `datetime` objects (from file modification timestamps)
   - The `_normalize_date_for_sorting()` function in `generator.py` handles comparison between these types by converting `date` to `datetime` at midnight
   - This preserves accurate time-of-day sorting for HTML pages while supporting date-only frontmatter

2. **Theme Persistence Strategy** - The dual persistence mechanism (URL parameters + localStorage) ensures theme selection works in both local file viewing (`file://` protocol) and web serving:
   - URL parameters persist across navigation when viewing local files
   - localStorage provides standard web persistence
   - System preference (`prefers-color-scheme`) serves as fallback
   - Pre-render script in `<head>` prevents flash of unstyled content

3. **CSS Architecture** - Complete separation of concerns across CSS files:
   - `base.css`: All layout, typography, and spacing rules (no colors)
   - Theme files: Only color variables (no layout or typography)
   - Font files: Only font family variables (`--font-sans` or `--font-mono`)
   - This separation allows any combination of theme + fonts without conflicts

4. **Tag Filtering Implementation** - Server-side tag filtering with dedicated index pages:
   - Controlled by `tags_as_link` config option (defaults to `True`)
   - When enabled: tags extracted from all posts and deduplicated, separate index pages generated for each tag at `/tags/{slug}/index.html`
   - When disabled: tags displayed as plain text, no `/tags/` folder created
   - Tag slugs handle special characters: "C++" → "c-plus-plus", "Machine Learning" → "machine-learning"
   - Tag descriptions loaded from `blog/tags/{slug}.md` (Markdown converted to HTML, no frontmatter)
   - Tag `.md` files excluded from main index (skipped during post parsing)
   - Tags clickable only in main index when enabled, not in tag-filtered views
   - Pagination applies to tag indices (respects `max_posts_per_index_page`)
   - Depth-aware asset URLs ensure CSS loads correctly from nested tag pages (`page_depth=2`)
   - Template receives `filtered_tag`, `tag_description_html`, and `page_depth` variables
   - Template checks `config.tags_as_link` to decide whether to render tags as links or plain text

## Design Decisions

1. **Static generation over dynamic** - Simpler deployment, works on any shared hosting
2. **Python over Node** - User preference, also good ecosystem for markdown processing
3. **Jinja2 templates** - Industry standard, easy to customize
4. **Modular CSS architecture** - Shared base.css + theme-specific color files, no build step required
5. **Named theme system** - Separate light/dark theme configuration allows mixing and matching
6. **Manual theme toggle + system preference** - Gives users control while respecting system defaults
7. **Dual persistence mechanism** - URL parameters for local files, localStorage for HTTP serving
8. **Relative paths by default** - Allows local viewing without web server, simplifies testing
9. **Official color palettes** - All themes use colors from official theme documentation (Catppuccin, Rose Pine, etc.)
10. **Separate font system** - Fonts defined independently from themes, allowing any font/theme combination
11. **Free fonts only** - All fonts loaded from reliable CDNs (Google Fonts, jsDelivr), no paid licenses required
12. **Font validation** - Config validation prevents errors, falls back gracefully to system fonts
13. **Optional pagination** - Defaults to single page (0), allows splitting for blogs with many posts
14. **Browser back button** - Post pages use `history.back()` to return to exact origin page, better UX than hardcoded index.html link

## Testing

To test changes:

```bash
# Build and inspect output
ghmd build -s ./example/blog -o ./example/output
# Or: python -m ghmd.cli build -s ./example/blog -o ./example/output

# Check specific file
cat ./example/output/index.html

# View in browser
open ./example/output/index.html  # macOS
xdg-open ./example/output/index.html  # Linux
```

**Note**: The `ghmd` command requires package installation (`pip install -e .`). Use `python -m ghmd.cli` if you only installed dependencies with `pip install -r requirements.txt`.

## Adding a New Feature

1. **New config option**: Add to `Config` dataclass in `config.py`
2. **New frontmatter field**: Add to `Post` dataclass in `parser.py`
3. **New template variable**: Pass in `generator.py` render calls
4. **New CLI command**: Add to `cli.py` with `@main.command()` decorator

## URL Mapping

| Source | Output | URL (when base_url="/") |
|--------|--------|-------------------------|
| `blog/post.md` | `output/post.html` | `post.html` |
| `blog/dir/post.md` | `output/dir/post.html` | `dir/post.html` |
| `blog/images/x.png` | `output/images/x.png` | `images/x.png` |

**Note:** When `base_url` is `/` (default), the generator uses relative paths (e.g., `post.html`) for local viewing. When deploying with a custom `base_url`, paths are prefixed accordingly (e.g., `/blog/post.html` if `base_url: /blog`).

## Contact / Origin

This project was designed and built with Claude (Anthropic) in December 2025.
Original requirements: Self-hosted blog from private GitHub repo, deployed to shared hosting via SFTP.
