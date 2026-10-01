import datetime as dt
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

import new_post
from new_post import PostError, app, create_post, make_slug, render_post

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


@pytest.mark.parametrize(
    "category",
    ["null", "true", "yes", "on", "no", "off", "y", "n", "2026", "1.0", "1_000", "0x1f", "2026-10-01"],
)
def test_render_post_quotes_categories_yaml_would_retype(category):
    # Unquoted, these load as bool/None/int/float/date and MkDocs aborts the build.
    meta = frontmatter(render_post("Hi", "hi", [category], True, TODAY))
    assert meta["categories"] == [category]


@pytest.mark.parametrize("slug", ["2026", "true", "null", "2026-10-01"])
def test_render_post_quotes_slugs_yaml_would_retype(slug):
    # Material requires a string slug; an int/bool/date one aborts the build.
    assert frontmatter(render_post("Hi", slug, [], True, TODAY))["slug"] == slug


def test_create_post_derived_numeric_slug_stays_a_string(tmp_path):
    path = create_post("2026", [], None, True, tmp_path, TODAY)
    assert frontmatter(path.read_text(encoding="utf-8"))["slug"] == "2026"


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


def test_create_post_rejects_overlong_slug(tmp_path):
    with pytest.raises(PostError, match="invalid --slug"):
        create_post("Title", [], "a" * 81, True, tmp_path, TODAY)
    assert list(tmp_path.iterdir()) == []


def test_create_post_reports_unwritable_posts_dir(tmp_path):
    tmp_path.chmod(0o500)
    try:
        with pytest.raises(PostError, match="could not create post"):
            create_post("Hi", [], None, True, tmp_path, TODAY)
    finally:
        tmp_path.chmod(0o700)


def test_create_post_removes_partial_file_when_write_fails(tmp_path, monkeypatch):
    real_open = Path.open

    class FailingWrite:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, _text):
            raise OSError(28, "No space left on device")

    monkeypatch.setattr(Path, "open", lambda self, *a, **k: FailingWrite(real_open(self, *a, **k)))
    with pytest.raises(PostError, match="could not write post"):
        create_post("Hi", [], None, True, tmp_path, TODAY)
    assert list(tmp_path.iterdir()) == []


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
