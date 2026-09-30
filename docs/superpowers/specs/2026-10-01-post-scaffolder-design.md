# Blog post scaffolder — design

## Goal

A single command that creates a correctly formatted draft post in `docs/posts/`.
It serves two callers:

- **The author**, from the terminal: `mise run post:new "My Title" -c python`.
- **Agents**, via the `write-blog` skill, so slug, dates, and the no-overwrite
  check are computed by code instead of re-derived from skill prose each time.

Success: one invocation yields a post that matches the existing format
(frontmatter, H1, `<!-- more -->` marker), never clobbers an existing post,
and is scriptable (no prompts, machine-readable output).

## Non-goals

- Interactive prompts.
- Writing post content (that stays with the `write-blog` skill).
- Supporting blog engines other than this repo's MkDocs Material blog.

## Components

### `scripts/new_post.py`

Executable Python script with a PEP 723 metadata block:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["typer==0.27.2", "python-slugify[anyascii]==9.1.2"]
# ///
```

Both dependencies are scoped to the script; `pyproject.toml` dependencies are
unchanged.

#### CLI

| Input | Default | Effect |
| --- | --- | --- |
| `TITLE` (positional, required) | — | H1 text and slug source |
| `--category` / `-c` (repeatable) | none | `categories:` entries, in the order given; none → `categories: []` |
| `--slug` | derived from title | Overrides slug and filename |
| `--publish` | off | Omits `draft: true` |

**Slug derivation** — `slugify(title, backend="anyascii")` from
[python-slugify](https://github.com/un33k/python-slugify), with the `anyascii`
extra for transliteration (both permissively licensed: MIT, ISC).

- `backend="anyascii"` must be passed explicitly: python-slugify's default
  `auto` backend picks Unidecode (GPL) or text-unidecode, never anyascii.
- Chosen over `inflection`, whose NFKD-based transliteration drops the Turkish
  dotless `ı` (`Ağır` → `agr`), and over hand-rolled NFKD plus a letter map.
- Verified outputs: `"Şişli'de Ağır Çözüm"` → `sisli-de-agir-cozum`,
  `"İstanbul ılık"` → `istanbul-ilik`, `"C++ & Rust: 2026 — Notlar…"` →
  `c-rust-2026-notlar`, `"!!!"` → `""`.

An explicit `--slug` is used verbatim after validating it matches
`^[a-z0-9]+(-[a-z0-9]+)*$`; otherwise exit 1.

**Output file** — `docs/posts/<slug>.md`, dates set to today (local time):

```markdown
---
draft: true
date:
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
categories:
  - python
authors:
  - hasansezertasan
slug: <slug>
---

# <Title>

TODO: intro paragraph.

<!-- more -->
```

With `--publish`, the `draft: true` line is omitted.

The `TODO: intro paragraph.` placeholder is a deliberate gate: the proselint
prek hook rejects it, so a scaffolded post cannot be committed until its intro
is written (author's decision, 2026-10-01).

**Input normalization** (added while planning, from the plan's Review Focus):

- Title: whitespace runs, including newlines, collapse to single spaces and
  the ends are trimmed; the result is written to the H1. A blank title exits 1
  with `title must not be empty`, even when `--slug` is given.
- Slug: capped at 80 characters on a word boundary
  (`max_length=80, word_boundary=True`), so long titles cannot exceed
  filesystem name limits.
- Categories: stripped, blanks dropped, duplicates removed keeping first
  order. Values matching `^[a-z0-9][a-z0-9._-]*$` (e.g. `astral.sh`) are
  written plain, as in existing posts; anything else is double-quoted so it
  cannot break the YAML (`"devops: ci"`, `"C++"`).

**Paths** — the posts directory is resolved from the script's location
(`Path(__file__).resolve().parent.parent / "docs" / "posts"`), so the command
works from any working directory. A `posts_dir` parameter on the core function
lets tests target a temporary directory.

#### Streams and exit codes

- Success: prints only the created file's path (relative to the repo root) to
  stdout; exit 0.
- All errors go to stderr with exit 1:
  - Title slugifies to an empty string → `can't derive a slug from title; pass --slug`.
  - Invalid `--slug`.
  - Target file already exists → message includes the existing path. The file
    is created with exclusive-create mode (`"x"`) so there is no
    check-then-write race.
  - `docs/posts/` does not exist.

### `scripts/test_new_post.py`

Pytest tests using typer's `CliRunner` against a temporary posts directory:

- Slugs: plain ASCII, Turkish (`"Şişli'de Ağır Çözüm"` → `sisli-de-agir-cozum`,
  `"İstanbul ılık"` → `istanbul-ilik`), punctuation/whitespace runs,
  leading/trailing symbols. `"👍 Ship It"` → `thumbsup-ship-it` pins the
  `anyascii` backend: text-unidecode (the `auto` fallback) yields `ship-it`.
- `--slug` override, and rejection of an invalid `--slug`.
- Repeated `-c` preserves order; no `-c` yields `categories: []`.
- `--publish` omits `draft: true`; default includes it.
- Existing file is not overwritten, exit 1, original content intact.
- Empty-slug title exits 1 with the `--slug` hint.
- Stdout contains only the path on success.

Transliterated Turkish test strings may trip the `typos` hook; if so, add the
specific words to `[tool.typos.default.extend-words]` in `pyproject.toml` with
a comment, matching the existing entries.

### mise tasks (`.config/mise.toml`)

```toml
[tasks."post:new"]
description = "Scaffold a new blog post draft"
run = "uv run scripts/new_post.py"

[tasks."post:test"]
description = "Test the post scaffolder"
run = "uv run --with pytest --with pyyaml --with-requirements scripts/new_post.py pytest scripts/"
```

mise forwards extra arguments to `run`, so `mise run post:new "Title" -c x`
works. `pytest` is never added to the project.

### Renovate (`.github/renovate.json`)

Renovate's native `pep723` manager has no default `managerFilePatterns`
(verified in Renovate's source: it is opt-in), so enable it for the scripts
directory:

```json
"pep723": { "managerFilePatterns": ["/^scripts/.+\\.py$/"] }
```

This keeps the pinned `typer` and `python-slugify` in `new_post.py` updated by
a native manager. Pinning them again in the `post:test` task would be a second
copy Renovate cannot see; to avoid it, `post:test` instead runs
`uv run --with pytest --with pyyaml --with-requirements scripts/new_post.py pytest scripts/`,
which reads the script's own inline metadata (verified with the installed
`uv`). PyYAML is test-only, used to parse the generated frontmatter.

### `write-blog` skill (`.agents/skills/write-blog/SKILL.md`)

`.claude/skills/write-blog` is a symlink to this file, so one edit covers both.

- Add a step before generation: if `scripts/new_post.py` exists, run
  `mise run post:new -- "<Title>" -c <category> ...` and use the printed path;
  on exit 1 for an existing file, ask the user whether to update that post or
  choose another slug.
- Then fill the body of the created file (replace the `TODO` intro, add
  sections below `<!-- more -->`).
- Keep the existing generic Hugo/Jekyll/MkDocs guidance as the fallback for
  repos without the script.

### `mkdocs.yml`

Exclude design docs from the published site:

```yaml
exclude_docs: |
  superpowers/
```

## Error handling summary

The command either creates exactly one new file and prints its path, or
creates nothing and exits 1 with a reason on stderr. It never modifies
existing files.

## Testing and verification

- `mise run post:test` passes.
- `mise run post:new "Deneme Yazısı" -c test` from a subdirectory creates
  `docs/posts/deneme-yazisi.md`; running it again exits 1. (Delete the file
  afterwards.)
- `mise run docs:build` succeeds and the built site contains no
  `superpowers/` pages.
- `prek -a` passes (shebang/executable, typos, editorconfig, markdownlint).
