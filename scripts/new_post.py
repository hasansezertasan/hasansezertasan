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
from typing import Annotated

import typer
from slugify import slugify

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "docs" / "posts"
AUTHOR = "hasansezertasan"
SLUG_MAX_LENGTH = 80
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Categories matching this are emitted as plain YAML scalars (e.g. `astral.sh`);
# anything else is double-quoted so it cannot change the frontmatter's structure.
# A leading letter rules out numbers and dates (`2026`, `0x1f`, `2026-10-01`).
PLAIN_CATEGORY = re.compile(r"^[a-z][a-z0-9._-]*$")
# Plain scalars YAML 1.1 (PyYAML, which MkDocs uses) loads as bool or None.
YAML_RESERVED = frozenset({"null", "true", "false", "yes", "no", "on", "off", "y", "n"})


class PostError(Exception):
    """The post cannot be created; the message is shown to the user."""


def make_slug(title: str) -> str:
    # python-slugify's "auto" backend never picks anyascii, so name it explicitly.
    return slugify(title, backend="anyascii", max_length=SLUG_MAX_LENGTH, word_boundary=True)


def yaml_scalar(value: str) -> str:
    if PLAIN_CATEGORY.fullmatch(value) and value not in YAML_RESERVED:
        return value
    return json.dumps(value, ensure_ascii=False)


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
