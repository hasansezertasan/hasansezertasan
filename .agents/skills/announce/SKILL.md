---
name: announce
description: Format content for social/messaging channels (WhatsApp, Reddit, Twitter) with language and tone options. Use when the user wants to share something on social media, announce a project, or adapt content for different platforms. Triggers on "make this WhatsApp friendly", "format for Reddit", "announce on Twitter", "Turkish announcement", "Turkish version of announcement", "social media post".
---

# Announce

Adapt content for specific channels with appropriate length, tone, and language.

## Channels

### WhatsApp

- **Length**: 150-250 words max
- **Tone**: Casual, conversational, direct
- **Format**: Short paragraphs, line breaks between sections, 1-2 relevant emojis
- **Links**: Full URLs on separate lines (no markdown)
- **No**: Headers, bullet points, code blocks

### Reddit

- **Length**: 150-300 words for post body
- **Tone**: Community-friendly, slightly technical for dev subs
- **Format**: Markdown supported, use headers sparingly
- **Structure**: Hook → Problem → Solution → Links
- **Subreddit hints**: r/Python, r/commandline, r/dotfiles, r/homebrew, etc.

### Twitter/X

- **Length**: Under 280 chars, or thread format
- **Tone**: Punchy, value-first
- **Format**: No markdown, use line breaks
- **Links**: Shortened or at end

## Language Support

When user requests a language (e.g., "Turkish", "Türkçe"):

- Translate naturally, not literally
- Keep technical terms in English where standard (e.g., "template", "CI/CD")
- Match local conventions (informal "sen" vs formal "siz" based on context)

## Workflow

1. **Identify source content** — Blog post, repo description, or conversation context
2. **Ask if unclear**: Channel? Language? Tone preference?
3. **Generate version** — Apply channel constraints
4. **Offer variants** — "Want a shorter version?" or "Need English too?"

## Example

**Input**: Blog about Homebrew/Scoop templates

**WhatsApp (Turkish)**:

```text
Homebrew ve Scoop için template repo'lar 🍺📦

Python CLI'ınızı macOS'ta `brew install`, Windows'ta `scoop install` ile
kurulabilir yapmak istiyorsanız:

tap-template — Homebrew: PyPI'dan formula scaffold'u, otomatik güncelleme
bucket-template — Scoop: binary release, pipx/uv shim desteği

👉 github.com/hasansezertasan/tap-template
👉 github.com/hasansezertasan/bucket-template
```

**Reddit (English)**:

```markdown
## Reusable templates for Homebrew taps and Scoop buckets

If you maintain a Python CLI and want users to `brew install` or `scoop install`
it without waiting for upstream — these templates handle the boilerplate:

- **tap-template**: Formula scaffolding from PyPI, bottle publishing, auto-updates
- **bucket-template**: Binary releases, pipx/uv shims, Windows CI

Both derive owner/repo from git remote, no manual substitution needed.

Links in comments.
```
