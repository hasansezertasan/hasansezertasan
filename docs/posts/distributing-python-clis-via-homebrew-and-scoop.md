---
draft: true
date:
  created: 2026-09-14
  updated: 2026-09-14
categories:
  - python
  - homebrew
  - scoop
  - devtools
slug: distributing-python-clis-via-homebrew-and-scoop
---

# Distributing Python CLIs with Homebrew and Scoop: From Curiosity to Templates

My Python CLI tools are already available through `uv`, but I use Homebrew on macOS and Scoop on Windows, so I wanted to understand how those ecosystems handle distribution. How do you write a formula? What does a manifest look like? And how do updates get automated?

<!-- more -->

## Exploring with agentic workflows

I explored those questions with agentic workflows. I used Claude Code to research and experiment with formula and manifest layouts, CI workflows, and update mechanisms. That work produced two working repositories:

- **[homebrew-tap](https://github.com/hasansezertasan/homebrew-tap)** — `brew install hasansezertasan/tap/cobo`
- **[scoop-bucket](https://github.com/hasansezertasan/scoop-bucket)** — `scoop bucket add hasansezertasan https://github.com/hasansezertasan/scoop-bucket` + `scoop install cobo`

## Turning It Into Templates

Once the process was repeatable, I turned both repositories into templates:

- **[tap-template](https://github.com/hasansezertasan/tap-template)** — Formula scaffolding from PyPI, bottle publishing, automated update workflows
- **[bucket-template](https://github.com/hasansezertasan/bucket-template)** — Binary releases, pipx/uv shim support, Windows CI tests

Start with the template, run `add_formula.py` or `add-manifest`, then push your changes. Your users can install the result with `brew install` or `scoop install`.
