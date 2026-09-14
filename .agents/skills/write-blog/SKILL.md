---
name: write-blog
description: Write a blog post matching the project's existing format (frontmatter, excerpt markers, categories). Use when the user wants to write a blog post, create a draft, or save content to their blog. Triggers on "write a blog post", "save to blog", "create a post about", "draft a blog".
---

# Write Blog

Write blog posts that match the existing format in the user's blog repository.

## Workflow

1. **Find the posts directory** — Look for `docs/posts/`, `content/posts/`, `_posts/`, or similar

2. **Read an existing post** — Check format, frontmatter structure, and conventions:

   ```bash
   ls docs/posts/
   ```

   Then read one to extract the pattern.

3. **Match the format** — Common elements to preserve:
   - Frontmatter fields (date, categories, slug, draft, authors)
   - Excerpt marker (`<!-- more -->`)
   - Heading style (H1 as title vs in frontmatter)
   - Category conventions

4. **Generate the post**:
   - Slug from title (lowercase, hyphenated)
   - `draft: true` by default
   - Today's date for created/updated
   - `<!-- more -->` after intro paragraph

5. **Save with descriptive filename** — Match slug: `distributing-python-clis-via-homebrew-and-scoop.md`

## Frontmatter Template

```yaml
---
draft: true
date:
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
categories:
  - category1
  - category2
slug: title-as-slug
---
```

## Structure

```markdown
# Title

Intro paragraph — hook the reader, state what this covers.

<!-- more -->

## Section 1

Content...

## Section 2

Content...

## Conclusion (optional)

Wrap-up, links, call to action.
```

## Notes

- Keep posts concise — 300-600 words is often ideal
- Include links to repos/PRs when referencing work
- Use code blocks sparingly and only when they add value
- After saving, remind user: "Saved with `draft: true` — remove when ready to publish"
