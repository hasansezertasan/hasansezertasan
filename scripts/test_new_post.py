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
