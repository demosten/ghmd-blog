"""
ghmd-blog: A static blog generator for GitHub markdown repositories.

Reads markdown files from a /blog directory, parses frontmatter,
and generates static HTML files for deployment to shared hosting.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .config import Config
from .parser import MarkdownParser
from .generator import BlogGenerator

__all__ = ["Config", "MarkdownParser", "BlogGenerator", "__version__"]
