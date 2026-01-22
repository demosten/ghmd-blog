# ghmd-blog

A static blog generator that reads markdown from a GitHub repository and deploys to shared hosting.

This project is strongly inspired by [plok.sh](https://www.plok.sh/). I recommend using plok.sh unless you need to self-host your blog (as I do). This is a complete rewrite in Python.

## Demo

See ghmd-blog in action at [demosten.com/ghmd-blog-demo](https://demosten.com/ghmd-blog-demo/)

## Features

- 📝 Write posts in Markdown with YAML frontmatter
- 🌐 Include standalone HTML pages alongside markdown posts
- 🔒 Works with private GitHub repositories
- 📤 Deploy to shared hosting via SFTP
- 🎨 17 professionally designed themes with mix-and-match light/dark modes
- 🌓 Manual light/dark theme toggle with automatic system preference detection
- 🔤 10 carefully selected free fonts with separate body/code configuration
- 🎨 Template override system for customizing header/footer without merge conflicts
- 🏷️ Tag filtering with dedicated index pages and optional descriptions
- 📑 Auto-generated table of contents
- ✨ Syntax highlighting for code blocks
- 📄 Index pagination with configurable posts per page
- 🚀 GitHub Actions for automatic deployment
- 🔗 Relative paths for local viewing (open output HTML files directly in browser)
- 📁 Automatic copying of all static files (images, PDFs, JSON, etc.)

## Quick Start

### Installation

**Option 1: Install as a package (recommended)**

```bash
# Clone the repository
git clone https://github.com/demosten/ghmd-blog.git
cd ghmd-blog

# Install the package (this makes the 'ghmd' command available)
pip install -e .
```

The `ghmd` command will now be available in your terminal.

**Option 2: Install dependencies only**

```bash
# Clone the repository
git clone https://github.com/demosten/ghmd-blog.git
cd ghmd-blog

# Install dependencies
pip install -r requirements.txt
```

With this option, use `python -m ghmd.cli` instead of `ghmd` for all commands.

### Initialize a New Blog

```bash
# If installed as package (Option 1)
ghmd init --source ./blog

# If using dependencies only (Option 2)
python -m ghmd.cli init --source ./blog
```

This creates a `blog` folder with an example configuration and post.

### Build Your Blog

```bash
# If installed as package (Option 1)
ghmd build --source ./blog --output ./output

# If using dependencies only (Option 2)
python -m ghmd.cli build --source ./blog --output ./output

# Override base_url for local development (optional)
ghmd build --source ./blog --output ./output --base-url /
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

## Documentation

For detailed documentation including configuration options, theme customization, deployment setup, and development guides, see [MANUAL.md](MANUAL.md).

## License

MIT License — see [LICENSE](LICENSE) for details.
