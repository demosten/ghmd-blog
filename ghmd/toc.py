"""
Table of contents generation for ghmd-blog.
"""

from typing import Optional


def generate_toc_html(headings: list[dict], min_level: int = 2, max_level: int = 4) -> str:
    """
    Generate HTML for a table of contents from headings.

    Args:
        headings: List of heading dicts with 'level', 'id', and 'text' keys.
        min_level: Minimum heading level to include (default: 2 for h2).
        max_level: Maximum heading level to include (default: 4 for h4).

    Returns:
        HTML string for the table of contents.
    """
    if not headings:
        return ""

    # Filter headings by level
    filtered = [h for h in headings if min_level <= h["level"] <= max_level]
    
    if not filtered:
        return ""

    lines = ['<nav class="toc" aria-label="Table of contents">', '<ul class="toc-list">']
    
    current_level = min_level
    
    for heading in filtered:
        level = heading["level"]
        
        # Adjust nesting
        while level > current_level:
            lines.append("<ul>")
            current_level += 1
        while level < current_level:
            lines.append("</ul></li>")
            current_level -= 1
        
        # Add the heading link
        lines.append(
            f'<li><a href="#{heading["id"]}">{heading["text"]}</a>'
        )
    
    # Close remaining open tags
    while current_level >= min_level:
        lines.append("</li></ul>")
        current_level -= 1
    
    lines.append("</nav>")
    
    return "\n".join(lines)


def count_headings(headings: list[dict], min_level: int = 2, max_level: int = 4) -> int:
    """
    Count headings within the specified level range.

    Args:
        headings: List of heading dicts.
        min_level: Minimum heading level to count.
        max_level: Maximum heading level to count.

    Returns:
        Number of headings in range.
    """
    return sum(1 for h in headings if min_level <= h["level"] <= max_level)
