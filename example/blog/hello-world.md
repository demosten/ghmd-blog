---
title: Hello World
date: 2025-12-01
update: 2025-12-03
description: My first blog post using ghmd-blog
tags: [intro, ghmd-blog]
author: demosten
---

# Welcome to my blog!

This is my **first post** using ghmd-blog. It's a static site generator that reads markdown from a GitHub repository and generates clean, fast HTML.

## Why ghmd-blog?

I wanted a simple way to:

- Write posts in Markdown
- Keep everything in a private GitHub repo
- Deploy to my shared hosting automatically
- Have full control over the output

## Features

Here's what ghmd-blog offers out of the box:

1. **Markdown support** — Write naturally with all standard markdown features
2. **Syntax highlighting** — Code blocks are beautifully highlighted
3. **Table of contents** — Auto-generated from your headings
4. **Dark mode** — Respects system preferences
5. **Fast** — Static HTML means instant page loads

## Code Example

Here's a Python snippet to demonstrate syntax highlighting:

```python
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}! Welcome to ghmd-blog."

if __name__ == "__main__":
    print(greet("World"))
```

And some JavaScript too:

```javascript
const posts = await fetch('/api/posts');
const data = await posts.json();
console.log(`Found ${data.length} posts`);
```

## What's Next?

Start writing! Create new `.md` files in your `blog` folder, push to GitHub, and your site updates automatically.

Happy blogging! 🚀
