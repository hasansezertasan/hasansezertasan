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
   ls <posts-directory>/
   ```

   Using the directory found in step 1, list its files and read an existing post to extract the pattern.

3. **Match the format** — Common elements to preserve:
   - Frontmatter fields (date, categories, slug, draft/published status, authors)
   - Excerpt marker (`<!-- more -->`)
   - Heading style (H1 as title vs in frontmatter)
   - Category conventions
   - Draft convention:
     - MkDocs / Hugo: `draft: true` in frontmatter
     - Jekyll: Save to `_drafts/` (or `published: false` in `_posts/`)
   - Filename convention:
     - MkDocs / Hugo: `<slug>.md`
     - Jekyll: `YYYY-MM-DD-<slug>.md` in `_posts/` (or `<slug>.md` in `_drafts/`)

4. **Generate the post**:
   - Slug from title (lowercase, hyphenated)
   - Draft handling matching layout conventions:
     - MkDocs / Hugo: `draft: true` in frontmatter
     - Jekyll: Save in `_drafts/` or set `published: false`
   - Today's date for created/updated or frontmatter date field
   - `<!-- more -->` after intro paragraph

5. **Save with filename matching layout conventions**:
   - MkDocs / Hugo: `<posts-directory>/<slug>.md` (e.g. `docs/posts/distributing-python-clis-via-homebrew-and-scoop.md`)
   - Jekyll: `_posts/YYYY-MM-DD-<slug>.md` (or `_drafts/<slug>.md` if saving as a draft)

## Frontmatter Template (MkDocs Example)

> Note: Match the frontmatter structure of the existing post read in step 2 (e.g. Jekyll uses `layout: post` and `title: "..."` in frontmatter; Hugo uses `title` and `date`).

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
- After saving, remind user how to publish based on layout:
  - MkDocs / Hugo: "Saved with `draft: true` — remove when ready to publish"
  - Jekyll: "Saved to `_drafts/<slug>.md` — move to `_posts/YYYY-MM-DD-<slug>.md` when ready to publish" (or remove `published: false`)
