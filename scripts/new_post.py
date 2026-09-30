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
