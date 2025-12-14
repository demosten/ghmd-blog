---
title: Getting Started with Markdown
date: 2025-12-03
description: A quick guide to writing markdown for your blog
tags: [tutorial, markdown]
author: Jane Doe, John Smith
---

# Getting Started with Markdown

Markdown is a lightweight markup language that lets you write formatted content using plain text. Here's everything you need to know to write great blog posts.

## Basic Formatting

You can make text **bold** with double asterisks, *italic* with single asterisks, or ***both*** with triple asterisks.

You can also use ~~strikethrough~~ with double tildes.

## Links and Images

Create links like this: [Visit GitHub](https://github.com)

Add images with similar syntax:

```markdown
![Alt text](path/to/image.jpg)
```

![That escalated quickly](images/escalate.jpg)

## Lists

Unordered lists use dashes or asterisks:

- First item
- Second item
  - Nested item
  - Another nested item
- Third item

Ordered lists use numbers:

1. Step one
2. Step two
3. Step three

## Blockquotes

> "The best way to predict the future is to invent it."
> — Alan Kay

## Tables

| Feature | Supported |
| ------- | --------- |
| Headers | ✓         |
| Bold    | ✓         |
| Code    | ✓         |
| Tables  | ✓         |

## Code

Inline code uses backticks: `const x = 42`

Code blocks use triple backticks with an optional language:

```python
def hello():
    print("Hello, World!")
```

## Frontmatter

Each post starts with YAML frontmatter between `---` markers:

```yaml
---
title: Your Post Title
date: 2025-01-15
description: A brief summary
tags: [tag1, tag2]
draft: false
---
```

That's it! Start writing your posts now.
