# Blog Post Scaffolder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `mise run post:new "Title" -c cat` command that creates a correctly formatted draft in `docs/posts/`, usable by the author and by the `write-blog` agent skill.

**Architecture:** One PEP 723 script, `scripts/new_post.py`, with three pure layers — `make_slug` (python-slugify, anyascii backend), `render_post` (frontmatter + skeleton text), `create_post` (validation + exclusive file create) — under a thin typer `main`. Tests live beside it in `scripts/test_new_post.py` and import it as a module. mise tasks wrap both; Renovate's native `pep723` manager keeps the inline pins current.

**Tech Stack:** Python 3.14, typer 0.27.2, python-slugify[anyascii] 9.1.2, pytest + PyYAML (test-only, via `uv run --with`), mise, uv, Renovate.

**Spec:** `docs/superpowers/specs/2026-10-01-post-scaffolder-design.md`

## Global Constraints

- Script dependencies live only in the PEP 723 block: `dependencies = ["typer==0.27.2", "python-slugify[anyascii]==9.1.2"]`, `requires-python = ">=3.14"`. `pyproject.toml` dependencies stay unchanged.
- Slugs come from `slugify(..., backend="anyascii")` — the backend is always named explicitly.
- Output file is `docs/posts/<slug>.md`, never overwritten (exclusive-create mode `"x"`).
- Success prints only the created path to stdout, exit 0. Every error goes to stderr as `error: <message>`, exit 1, and creates no file.
- The body placeholder is exactly `TODO: intro paragraph.` — proselint rejecting it is a deliberate gate (author's decision, 2026-10-01).
- Author is `hasansezertasan`; dates are today's local date for both `created` and `updated`.
- Never pin a dependency version in two places; test commands read pins from the script via `--with-requirements scripts/new_post.py`.
- Commits follow Conventional Commits; commit only the paths named in each task (`git commit -- <paths>`), because `.claude/settings.json` is staged by someone else and must stay out of these commits. No AI attribution trailers.

## Review Focus

1. **YAML-unsafe categories** (`-c "devops: ci"`, `-c "#tag"`, `-c "C++"`) — the frontmatter must still parse and yield exactly those strings; plain safe values like `astral.sh` stay unquoted to match existing posts. Pinned in Task 1 (`test_render_post_quotes_yaml_unsafe_categories`).
2. **Very long titles** — the slug/filename must not grow unbounded (filesystem limits give an unhandled `OSError`); cap at 80 chars on a word boundary. Pinned in Task 1 (`test_make_slug_caps_long_titles_on_a_word_boundary`).
3. **Titles with stray whitespace or newlines** (shell quoting, agent-generated input) — the H1 must be a single clean line. Pinned in Task 2 (`test_create_post_normalizes_title_whitespace`).
4. **Blank titles**, with or without `--slug` — must error, not write `#` as the heading. Pinned in Task 2 (`test_create_post_rejects_blank_title`).
5. **Duplicate or blank categories** (`-c python -c python -c ""`) — emitted once each, blanks dropped. Pinned in Task 2 (`test_create_post_dedupes_and_strips_categories`).

---

### Task 1: Slug and post rendering

**Files:**

- Create: `scripts/new_post.py`
- Create: `scripts/test_new_post.py`
- Modify: `.config/mise.toml` (add `post:test` task after `docs:build`)
- Modify: `.github/renovate.json` (enable `pep723` manager)

**Interfaces:**

- Consumes: nothing.
- Produces (in `scripts/new_post.py`):
  - `make_slug(title: str) -> str` — may return `""`.
  - `yaml_scalar(value: str) -> str`
  - `render_post(title: str, slug: str, categories: list[str], draft: bool, today: datetime.date) -> str`
  - Module constants `REPO_ROOT: Path`, `POSTS_DIR: Path`, `AUTHOR = "hasansezertasan"`, `SLUG_MAX_LENGTH = 80`.
  - mise task `post:test`.
  - Test helper `frontmatter(text: str) -> dict` and constant `TODAY = dt.date(2026, 10, 1)` in `scripts/test_new_post.py`.

- [ ] **Step 1: Create the script skeleton and the `post:test` task**

The skeleton must exist before the tests run, because the test command reads its PEP 723 block.

Create `scripts/new_post.py`:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["typer==0.27.2", "python-slugify[anyascii]==9.1.2"]
# ///
"""Scaffold a new blog post draft in docs/posts/."""
```

Make it executable (the `check-executables-have-shebangs` prek hook requires the shebang, which is present):

```bash
chmod +x scripts/new_post.py
```

In `.config/mise.toml`, insert after the `[tasks."docs:build"]` block:

```toml
[tasks."post:test"]
description = "Test the post scaffolder"
run = "uv run --with pytest --with pyyaml --with-requirements scripts/new_post.py pytest scripts/"
```

- [ ] **Step 2: Write the failing tests**

Create `scripts/test_new_post.py`:

```python
import datetime as dt

import pytest
import yaml

from new_post import make_slug, render_post

TODAY = dt.date(2026, 10, 1)


def frontmatter(text: str) -> dict:
    _, block, _ = text.split("---\n", 2)
    return yaml.safe_load(block)


@pytest.mark.parametrize(
    ("title", "slug"),
    [
        ("Hello World", "hello-world"),
        ("Şişli'de Ağır Çözüm", "sisli-de-agir-cozum"),
        ("İstanbul ılık", "istanbul-ilik"),
        ("C++ & Rust: 2026 — Notlar…", "c-rust-2026-notlar"),
        ("  --Leading and trailing!!  ", "leading-and-trailing"),
        # anyascii gives "thumbsup"; text-unidecode (slugify's default) drops the emoji.
        ("👍 Ship It", "thumbsup-ship-it"),
        ("!!!", ""),
    ],
)
def test_make_slug(title, slug):
    assert make_slug(title) == slug


def test_make_slug_caps_long_titles_on_a_word_boundary():
    slug = make_slug("word " * 40)
    assert len(slug) <= 80
    assert slug.endswith("word")


def test_render_post_draft_with_categories():
    assert render_post("Hello World", "hello-world", ["python", "uv"], True, TODAY) == (
        "---\n"
        "draft: true\n"
        "date:\n"
        "  created: 2026-10-01\n"
        "  updated: 2026-10-01\n"
        "categories:\n"
        "  - python\n"
        "  - uv\n"
        "authors:\n"
        "  - hasansezertasan\n"
        "slug: hello-world\n"
        "---\n"
        "\n"
        "# Hello World\n"
        "\n"
        "TODO: intro paragraph.\n"
        "\n"
        "<!-- more -->\n"
    )


def test_render_post_published_without_categories():
    meta = frontmatter(render_post("Hi", "hi", [], False, TODAY))
    assert "draft" not in meta
    assert meta["categories"] == []


def test_render_post_quotes_yaml_unsafe_categories():
    categories = ["astral.sh", "devops: ci", "#tag", "C++", "Türkçe"]
    text = render_post("Hi", "hi", categories, True, TODAY)
    assert "  - astral.sh\n" in text
    meta = frontmatter(text)
    assert meta["categories"] == categories
    assert meta["slug"] == "hi"
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `mise run post:test`
Expected: collection error, `ImportError: cannot import name 'make_slug' from 'new_post'`.

- [ ] **Step 4: Implement slug and rendering**

Replace `scripts/new_post.py` with:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["typer==0.27.2", "python-slugify[anyascii]==9.1.2"]
# ///
"""Scaffold a new blog post draft in docs/posts/."""

import datetime as dt
import json
import re
from pathlib import Path

from slugify import slugify

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "docs" / "posts"
AUTHOR = "hasansezertasan"
SLUG_MAX_LENGTH = 80
# Categories matching this are emitted as plain YAML scalars (e.g. `astral.sh`);
# anything else is double-quoted so it cannot change the frontmatter's structure.
PLAIN_CATEGORY = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def make_slug(title: str) -> str:
    # python-slugify's "auto" backend never picks anyascii, so name it explicitly.
    return slugify(title, backend="anyascii", max_length=SLUG_MAX_LENGTH, word_boundary=True)


def yaml_scalar(value: str) -> str:
    return value if PLAIN_CATEGORY.fullmatch(value) else json.dumps(value, ensure_ascii=False)


def render_post(title: str, slug: str, categories: list[str], draft: bool, today: dt.date) -> str:
    lines = ["---"]
    if draft:
        lines.append("draft: true")
    lines += ["date:", f"  created: {today.isoformat()}", f"  updated: {today.isoformat()}"]
    if categories:
        lines += ["categories:", *(f"  - {yaml_scalar(category)}" for category in categories)]
    else:
        lines.append("categories: []")
    lines += ["authors:", f"  - {AUTHOR}", f"slug: {slug}", "---", ""]
    lines += [f"# {title}", "", "TODO: intro paragraph.", "", "<!-- more -->", ""]
    return "\n".join(lines)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `mise run post:test`
Expected: `11 passed`.

Then confirm the backend test is load-bearing: temporarily change `backend="anyascii"` to `backend="auto"`, run `mise run post:test`, and expect exactly one failure (`test_make_slug[\U0001f44d Ship It-thumbsup-ship-it]` — pytest escapes the emoji in the ID — got `ship-it`). Revert the change and re-run: `11 passed`.

- [ ] **Step 6: Enable Renovate's `pep723` manager**

Renovate's `pep723` manager ships with empty `managerFilePatterns` (opt-in), so the inline pins are invisible to it until enabled. Replace `.github/renovate.json` with:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["github>hasansezertasan/renovate-config:python"],
  "pep723": {
    "managerFilePatterns": ["/^scripts/.+\\.py$/"]
  }
}
```

Run: `prek run --files .github/renovate.json .config/mise.toml scripts/new_post.py scripts/test_new_post.py`
Expected: every hook `Passed` or `Skipped` (`check-renovate` validates the config against the schema).

- [ ] **Step 7: Commit**

```bash
git add scripts/new_post.py scripts/test_new_post.py .config/mise.toml .github/renovate.json
git commit -m "feat: add post slug and frontmatter rendering" -- scripts/new_post.py scripts/test_new_post.py .config/mise.toml .github/renovate.json
```

---

### Task 2: Post creation and the `post:new` CLI

**Files:**

- Modify: `scripts/new_post.py` (add `PostError`, `SLUG_PATTERN`, `create_post`, typer `app`/`main`)
- Modify: `scripts/test_new_post.py` (add creation and CLI tests)
- Modify: `.config/mise.toml` (add `post:new` task before `post:test`)

**Interfaces:**

- Consumes: `make_slug`, `render_post`, `POSTS_DIR`, `REPO_ROOT` from Task 1; `frontmatter`, `TODAY` test helpers from Task 1.
- Produces:
  - `class PostError(Exception)` — message is user-facing.
  - `create_post(title: str, categories: list[str], slug: str | None, draft: bool, posts_dir: Path, today: datetime.date) -> Path` — raises `PostError`.
  - `app: typer.Typer` with a single command `main(title, --category/-c, --slug, --publish)`.
  - mise task `post:new`. Task 3's skill text invokes `mise run post:new -- "<Title>" -c <category>`.

- [ ] **Step 1: Write the failing tests**

In `scripts/test_new_post.py`, replace the import block:

```python
import datetime as dt

import pytest
import yaml

from new_post import make_slug, render_post
```

with:

```python
import datetime as dt

import pytest
import yaml
from typer.testing import CliRunner

import new_post
from new_post import PostError, app, create_post, make_slug, render_post
```

Append to the end of the file:

```python
def test_create_post_writes_file(tmp_path):
    path = create_post("Şişli'de Ağır Çözüm", ["python"], None, True, tmp_path, TODAY)
    assert path == tmp_path / "sisli-de-agir-cozum.md"
    text = path.read_text(encoding="utf-8")
    assert "\n# Şişli'de Ağır Çözüm\n" in text
    assert frontmatter(text)["slug"] == "sisli-de-agir-cozum"


def test_create_post_slug_override(tmp_path):
    path = create_post("Anything", [], "custom-slug", True, tmp_path, TODAY)
    assert path.name == "custom-slug.md"
    assert frontmatter(path.read_text(encoding="utf-8"))["slug"] == "custom-slug"


@pytest.mark.parametrize("bad", ["Bad_Slug", "has space", "-lead", "double--hyphen", ""])
def test_create_post_rejects_invalid_slug(tmp_path, bad):
    with pytest.raises(PostError, match="invalid --slug"):
        create_post("Title", [], bad, True, tmp_path, TODAY)
    assert list(tmp_path.iterdir()) == []


def test_create_post_empty_slug_hints_at_flag(tmp_path):
    with pytest.raises(PostError, match="pass --slug"):
        create_post("!!!", [], None, True, tmp_path, TODAY)


@pytest.mark.parametrize("slug", [None, "blank"])
def test_create_post_rejects_blank_title(tmp_path, slug):
    with pytest.raises(PostError, match="title must not be empty"):
        create_post(" \n ", [], slug, True, tmp_path, TODAY)
    assert list(tmp_path.iterdir()) == []


def test_create_post_normalizes_title_whitespace(tmp_path):
    path = create_post("  Multi\n  line   title ", [], None, True, tmp_path, TODAY)
    assert path.name == "multi-line-title.md"
    assert "\n# Multi line title\n" in path.read_text(encoding="utf-8")


def test_create_post_dedupes_and_strips_categories(tmp_path):
    path = create_post("Hi", ["python", " uv ", "python", ""], None, True, tmp_path, TODAY)
    assert frontmatter(path.read_text(encoding="utf-8"))["categories"] == ["python", "uv"]


def test_create_post_refuses_to_overwrite(tmp_path):
    existing = tmp_path / "hello-world.md"
    existing.write_text("original", encoding="utf-8")
    with pytest.raises(PostError, match="post already exists"):
        create_post("Hello World", [], None, True, tmp_path, TODAY)
    assert existing.read_text(encoding="utf-8") == "original"


def test_create_post_missing_posts_dir(tmp_path):
    with pytest.raises(PostError, match="posts directory not found"):
        create_post("Hi", [], None, True, tmp_path / "nope", TODAY)


@pytest.fixture
def posts_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(new_post, "POSTS_DIR", tmp_path)
    return tmp_path


def test_cli_creates_draft_and_prints_only_the_path(posts_dir):
    result = CliRunner().invoke(app, ["Hello World", "-c", "python", "--category", "uv"])
    assert result.exit_code == 0, result.stderr
    assert result.stdout == f"{posts_dir / 'hello-world.md'}\n"
    assert result.stderr == ""
    meta = frontmatter((posts_dir / "hello-world.md").read_text(encoding="utf-8"))
    assert meta["draft"] is True
    assert meta["categories"] == ["python", "uv"]
    assert meta["date"]["created"] == dt.date.today()


def test_cli_publish_and_slug(posts_dir):
    result = CliRunner().invoke(app, ["Hello", "--slug", "hi-there", "--publish"])
    assert result.exit_code == 0, result.stderr
    assert "draft" not in frontmatter((posts_dir / "hi-there.md").read_text(encoding="utf-8"))


def test_cli_existing_post_exits_1_on_stderr(posts_dir):
    (posts_dir / "hello.md").write_text("original", encoding="utf-8")
    result = CliRunner().invoke(app, ["Hello"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr.startswith("error: post already exists:")
    assert (posts_dir / "hello.md").read_text(encoding="utf-8") == "original"


def test_cli_empty_slug_exits_1(posts_dir):
    result = CliRunner().invoke(app, ["!!!"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr == "error: can't derive a slug from title; pass --slug\n"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `mise run post:test`
Expected: collection error, `ImportError: cannot import name 'PostError' from 'new_post'`.

- [ ] **Step 3: Implement creation and the CLI**

In `scripts/new_post.py`, replace the imports:

```python
import datetime as dt
import json
import re
from pathlib import Path

from slugify import slugify
```

with:

```python
import datetime as dt
import json
import re
from pathlib import Path
from typing import Annotated

import typer
from slugify import slugify
```

Insert after the `SLUG_MAX_LENGTH = 80` line:

```python
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
```

Insert after the `PLAIN_CATEGORY = ...` line (before `def make_slug`):

```python


class PostError(Exception):
    """The post cannot be created; the message is shown to the user."""
```

Append to the end of the file:

```python


def create_post(
    title: str,
    categories: list[str],
    slug: str | None,
    draft: bool,
    posts_dir: Path,
    today: dt.date,
) -> Path:
    title = " ".join(title.split())
    if not title:
        raise PostError("title must not be empty")
    categories = list(dict.fromkeys(c.strip() for c in categories if c.strip()))
    if slug is None:
        slug = make_slug(title)
        if not slug:
            raise PostError("can't derive a slug from title; pass --slug")
    elif not SLUG_PATTERN.fullmatch(slug):
        raise PostError(f"invalid --slug {slug!r}; use lowercase letters, digits, and single hyphens")
    if not posts_dir.is_dir():
        raise PostError(f"posts directory not found: {posts_dir}")
    path = posts_dir / f"{slug}.md"
    try:
        with path.open("x", encoding="utf-8") as file:
            file.write(render_post(title, slug, categories, draft, today))
    except FileExistsError:
        raise PostError(f"post already exists: {path}") from None
    return path


app = typer.Typer(add_completion=False)


@app.command()
def main(
    title: Annotated[str, typer.Argument(help="Post title, used for the H1 and the slug.")],
    category: Annotated[
        list[str] | None,
        typer.Option("--category", "-c", help="Category; repeat for several."),
    ] = None,
    slug: Annotated[str | None, typer.Option(help="Override the slug derived from the title.")] = None,
    publish: Annotated[bool, typer.Option("--publish", help="Omit `draft: true`.")] = False,
) -> None:
    """Scaffold a new blog post draft in docs/posts/."""
    try:
        path = create_post(title, category or [], slug, not publish, POSTS_DIR, dt.date.today())
    except PostError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1) from None
    typer.echo(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path)


if __name__ == "__main__":
    app()
```

In `.config/mise.toml`, insert before the `[tasks."post:test"]` block:

```toml
[tasks."post:new"]
description = "Scaffold a new blog post draft"
run = "uv run scripts/new_post.py"
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `mise run post:test`
Expected: `29 passed`.

- [ ] **Step 5: Verify end to end from a subdirectory**

Run:

```bash
cd docs && mise run -q post:new "Deneme Yazısı" -c test; echo "exit=$?"; cd ..
```

Expected: stdout `docs/posts/deneme-yazisi.md`, `exit=0`.

Run: `cat docs/posts/deneme-yazisi.md`
Expected: frontmatter with `draft: true`, today's date twice, `categories:` / `- test`, `authors:` / `- hasansezertasan`, `slug: deneme-yazisi`, then `# Deneme Yazısı`, `TODO: intro paragraph.`, `<!-- more -->`.

Run: `mise run -q post:new "Deneme Yazısı"; echo "exit=$?"`
Expected: stderr `error: post already exists: .../docs/posts/deneme-yazisi.md`, `exit=1`.

Run: `mise run docs:build 2>&1 | tail -3`
Expected: `Documentation built in …`, no error (the scaffolded draft builds).

Run: `prek run --files docs/posts/deneme-yazisi.md 2>&1 | grep -E "Failed|annotations"`
Expected: `A linter for prose....Failed` with `annotations.misc` on the `TODO` line — the intended gate.

Then clean up: `rm docs/posts/deneme-yazisi.md && rm -rf site` and confirm `git status --short` shows only the Task 2 files plus the pre-existing staged `.claude/settings.json`.

- [ ] **Step 6: Lint and commit**

Run: `prek run --files scripts/new_post.py scripts/test_new_post.py .config/mise.toml`
Expected: every hook `Passed` or `Skipped`.

```bash
git add scripts/new_post.py scripts/test_new_post.py .config/mise.toml
git commit -m "feat: add post:new command to scaffold blog posts" -- scripts/new_post.py scripts/test_new_post.py .config/mise.toml
```

---

### Task 3: Make the `write-blog` skill use the scaffolder

**Files:**

- Modify: `.agents/skills/write-blog/SKILL.md` (steps 4–5; `.claude/skills/write-blog` is a symlink to this directory)

**Interfaces:**

- Consumes: `mise run post:new -- "<Title>" [-c <category>]... [--slug <slug>]` from Task 2 — prints the created path on stdout (exit 0), or `error: post already exists: <path>` on stderr (exit 1).
- Produces: nothing code-facing.

- [ ] **Step 1: Add the scaffolder step**

In `.agents/skills/write-blog/SKILL.md`, replace the line:

```markdown
4. **Generate the post**:
```

with:

````markdown
4. **Scaffold with the repo's command, if it has one** — If `scripts/new_post.py` exists, create the file with it instead of writing frontmatter by hand:

    ```bash
    mise run post:new -- "<Title>" -c <category> -c <category>
    ```

    - Use the categories chosen from existing posts; add `--slug <slug>` only when the user wants a specific one, and `--publish` only when they ask to publish immediately.
    - On success it prints the created path — open that file, replace the `TODO: intro paragraph.` line with the intro, and write the sections below `<!-- more -->`. Keep the frontmatter it generated. The pre-commit prose linter rejects a leftover `TODO`, so the intro must be written before committing.
    - If it exits 1 with `error: post already exists: <path>`, ask whether to update that post or choose another slug; never delete the existing file to make room.
    - Then skip steps 5 and 6 below — they are the manual fallback for repositories without the command.

5. **Generate the post** (manual fallback):
````

Then renumber the following heading `5. **Check the destination, then save with a filename matching layout conventions**` to `6. **Check the destination, then save with a filename matching layout conventions**`.

- [ ] **Step 2: Verify the skill text**

Run: `grep -n -E "^[0-9]\. \*\*" .agents/skills/write-blog/SKILL.md`
Expected: six numbered steps, 1 through 6, with 4 being `Scaffold with the repo's command, if it has one` and 5 being `Generate the post** (manual fallback)`.

Run: `prek run --files .agents/skills/write-blog/SKILL.md`
Expected: every hook `Passed` or `Skipped` (proselint excludes `.agents/`, so the literal `TODO` is fine here).

- [ ] **Step 3: Commit**

```bash
git add .agents/skills/write-blog/SKILL.md
git commit -m "docs(write-blog): scaffold posts with post:new when available" -- .agents/skills/write-blog/SKILL.md
```

Whole-plan test command (for the final `task-done` run of every task): `mise run post:test`.
