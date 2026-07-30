---
marp: true
lang: en-US
class: invert
header: "Toolception"
footer: "Slides by [@hasansezertasan]"
paginate: true
_paginate: false
---
<!-- markdownlint-disable MD035 -->
<!-- headingDivider: 3 -->

# Toolception <!-- fit -->

<hr>

[@hasansezertasan]

<!-- transition: slide -->

## About this talk

Prepared for a **Hackday at [Paket Mutfak]**, where I work.

📅 Wednesday, May 7, 2025 ⋅ 4:00 – 5:15pm

A tour of the command-line tools I use every day.

<!-- transition: slide -->

## Agenda

- Management Tools: `brew`, `mise`, `uv`
- Task Runners: `xc`
- Check stuff: `typos`, `taplo`, `shellcheck`

## Tools

![bg right 60%](https://cdn.jsdelivr.net/npm/@svgmoji/twemoji@2.0.0/svg/1F4BB.svg)

- A `brew` summary
- What does `mise` en place mean?
- Is `uv` bad for our health?
- What is `xc`?
- No more `typos`.
- WTF is `taplo`?
- Check shell scripts with `shellcheck`.

<!-- transition: melt -->

## A `brew` summary

<!-- _backgroundColor: #10151e -->
![bg left 60%](https://svgl.app/library/homebrew.svg)

The Missing Package Manager for macOS (or Linux).

<!-- transition: slide -->

## Install `brew` with

<!-- _backgroundColor: #10151e -->

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## What does it do?

<!-- _backgroundColor: #10151e -->
Manage Packages

A package is a piece of software (CLI, GUI, Script, etc.) that is bundled together with all the files and instructions needed to install it.

```bash
# A CLI Tool (Formula)
brew install uv

# A GUI Tool (Cask)
brew install --cask visual-studio-code
```

When I set up a new machine, the first thing I do is install `brew` and then install all the packages by running `brew bundle`.

I use `brew` to manage my packages globally (OS level).

## Why am I telling you this?

<!-- _backgroundColor: #10151e -->

We manage many things with `brew`:

- CLI Tools
- GUI Tools
- Fonts
- Applications
- Services

In the next slide, we will see different package managers. We need a common understanding of what brew is and what it does.

<!-- transition: melt -->

## What does `mise` en place mean?

<!-- _backgroundColor: #141a24 -->
![bg right 60%](https://raw.githubusercontent.com/jdx/mise/refs/heads/main/docs/public/android-chrome-512x512.png)

> "Everything in its place"

A culinary phrase that refers to the setup required before cooking.

`mise` pronounced like "meez".

Author: [Jeff Dickey][jdx] - Working at [Figma]

<!-- transition: slide -->

## Problem

<!-- _backgroundColor: #141a24 -->
When collaborating in a team, maintaining a consistent environment for everyone is crucial. Furthermore, different projects often demand specific versions of tools.

Automating repetitive tasks within the codebase is equally beneficial, making task management an essential component.

## Install `mise` with

<!-- _backgroundColor: #141a24 -->

```bash
# brew
brew install mise

# scoop (windows)
scoop install mise

# installer script
curl https://mise.run | sh
```

Check out the [documentation](https://mise.jdx.dev/installing-mise.html) for more details. It has too many options to list here.

> Scoop is a command-line installer for Windows. It is similar to Homebrew, but it is designed specifically for Windows.

## What does it do? (as a package manager)

<!-- _backgroundColor: #141a24 -->

> "Polyglot tool manager."

It replaces: `asdf`, `nvm`, `pyenv`, `goenv`, `rbenv`, `rustup`, and more.

It is aware of many standard files: `.python-version`, `.tool-versions`, and more.

It is very performant and fast. It is written in Rust. It Installs tools in parallel.

Interactive UI for installing tools. (`mise use` and hit enter)

There is a very well structured VSCode extension for `mise`.

## How do I use mise as a package manager?

<!-- _backgroundColor: #141a24 -->

I use `mise` to manage:

- Programming Language Installs with versions (`mise use go@<version>`)
- PyPI Registered CLI tools (replaces `pipx` and `uvx` with `mise use pipx:<package>`)
- NPM Registered CLI tools (partially replaces `npm` with `mise use npm:<package>`)
- Install CLI Tools based on Go, Ruby, Rust (Cargo), and more.

Mise pins the tools inside a file called `mise.toml` in the root of your project or `~/.config/mise/config.toml` in your home directory for global installs.

I use `mise` to manage my tools in both my projects and globally.

Mise can use both pipx and uv.

## What does it do? (as a task runner)

<!-- _backgroundColor: #141a24 -->

> "Frontend to your development environment."

Replaces: `make`, `just`, `npm run`, and more.

Interactive UI for running tasks.

I use `mise` to manage my global tasks. Register globally available tasks.

Dependencies between tasks.

Task aliases.

Run tasks on file changes.

... and more.

## A simple Mise Task

<!-- _backgroundColor: #141a24 -->

`mise.toml` file in the root of your project.

```toml
[tasks."hello-world"]
alias = "hw"
description = "Hello World"
run = "echo 'Hello World!'"
```

Run the task with:

```bash
mise run hw
```

## What does it do? (as an environment variable manager)

<!-- _backgroundColor: #141a24 -->

> "Like direnv it manages environment variables for different project directories."

I never used `direnv` or `mise`'s environment features.

I don't have much to say about this feature.

## Want to know more?

<!-- _backgroundColor: #141a24 -->

Mise has a great [documentation][mise-docs]. It is very well structured and easy to read.

Quotes in the previous slide are from this YouTube Video: [Jeff Dickey - Mise, Usage, and Pitchfork and the Future of Polyglot Tools](https://www.youtube.com/watch?v=XDAfpzjBYJQ&ab_channel=devtools-fm).

[Using Mise for All the Things](https://jarv.org/posts/mise/)

[Mise: Dev tools, env vars, task runner | Hacker News](https://news.ycombinator.com/item?id=42347917)

[mise-en-place (dev tools, env vars, task runner) — Tuto build](https://gdevops.frama.io/dev/tuto-build/mise/mise.html)

[Automate Dev Environments with Mise Guide | Medium](https://rgeraskin.medium.com/dev-env-with-mise-45a062707705)

<!-- transition: melt -->

## Is `uv` bad for our health?

<!-- _backgroundColor: #171e2a -->
![bg left 60%](https://raw.githubusercontent.com/astral-sh/uv/1ec193569349f2e4b411984262de86905d2c0e53/docs/assets/logo-letter.svg)

Not in the [Astral][astral-sh] dimension.

<!-- transition: slide -->

## What does it do?

<!-- _backgroundColor: #171e2a -->

Replaces: `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv`, and more.

10-100x faster than pip.

Runs and installs tools published as Python packages.

Disk-space efficient, with a global cache for dependency deduplication.

Supports macOS, Linux, and Windows.

<!-- transition: melt -->

## What is `xc`?

<!-- _backgroundColor: #1e2737 -->
![bg left 60%](https://raw.githubusercontent.com/joerdav/xc/refs/heads/main/doc/static/favicon.ico)

`xc` is a task runner similar to `Make` or `npm run`, that aims to be more discoverable and approachable.

<!-- transition: slide -->

## What does it do?

<!-- _backgroundColor: #1e2737 -->

Provide a simple way to run tasks defined in a `README.md` file.

The problem xc is intended to solve is scripts or tasks maintained separately from their documentation.

Often a Makefile or a package.json will contain some useful scripts for developing on a project, then the README.md will surface and describe these scripts.

In such a case, since the documentation is separate, it may not be updated when scripts are changed or added. xc aims to solve this by defining the scripts inline with the documentation.

## Install `xc` with

<!-- _backgroundColor: #1e2737 -->

```bash
# brew
brew tap joerdav/xc
brew install xc
# mise (globally)
mise use xc -g
```

### Let's start with a simple example

<!-- _backgroundColor: #1e2737 -->

```markdown
# Project Name

Project Description

## Tasks

Each heading under `Tasks` is treated as a task by xc

### `setup`

run: once

    ```bash
    echo "Foundational Setup..."
    ```
```

### Run the task with

<!-- _backgroundColor: #1e2737 -->

Directly run the task with:

```bash
xc setup
```

Interactively run the task with:

```bash
xc
```

<!-- transition: slide -->

### Dependent Tasks

<!-- _backgroundColor: #212b3d -->

```markdown
# Project Name
## Tasks
### `install`

Requires: setup

run: once

    ```bash
    echo "Project setup..."
    ```
...
```

<!-- transition: slide -->

### Want to know more?

<!-- _backgroundColor: #212b3d -->

- [xc]
- [GitHub Action][xc-gha]
- [Alternatives](https://github.com/joerdav/xc/issues/116)

<!-- transition: melt -->

## No more `typos`

<!-- _backgroundColor: #1a2231 -->
![bg right 60%](https://svgl.app/library/rust_dark.svg)

Rust-based source code spell checker

## WTF is `taplo`?

<!-- _backgroundColor: #242f43 -->

![bg left 60%](https://raw.githubusercontent.com/tamasfe/taplo/refs/heads/master/taplo-icon.png)

A TOML toolkit written in Rust

## Check shell scripts with `shellcheck`

<!-- _backgroundColor: #283449 -->

ShellCheck, a static analysis tool for shell scripts.

![bg right 60%](https://svgl.app/library/bash_dark.svg)

## Questions

Do you have any questions?

<!-- transition: swipe -->

## What is the best tool for you?

- `brew`, `mise`, and `uv` overlap.
- `xc` and `mise` overlap on project-level tasks.

<!-- transition: swipe -->

## See You Next Time :wave:

- Awesome:
  - `uv run --script`
  - `zoxide` is a smarter `cd`
  - `fzf` is a fuzzy finder.
  - `ripgrep` (aka `rg`, a faster `grep`)
- Visual Tools:
  - `marp`
  - `mermaid`
- HTTP Tools:
  - `httpyac`
  - `hurl`

<!-- transition: swipe -->

## References

- [brew]
- [scoop]
- [mise]
- [uv]
- [xc]
- [typos]
- [taplo]
- [shellcheck]
- [zoxide]
- [fzf]
- [ripgrep]
- [marp]
- [mermaid]
- [httpyac]
- [hurl]

[brew]: https://brew.sh
[scoop]: https://scoop.sh/
[mise]: https://github.com/jdx/mise
[uv]: https://github.com/astral-sh/uv
[xc]: https://github.com/joerdav/xc
[typos]: https://github.com/crate-ci/typos
[taplo]: https://github.com/tamasfe/taplo
[shellcheck]: https://github.com/koalaman/shellcheck
[zoxide]: https://github.com/ajeetdsouza/zoxide
[fzf]: https://github.com/junegunn/fzf
[ripgrep]: https://github.com/BurntSushi/ripgrep
[marp]: https://github.com/marp-team/marp
[mermaid]: https://github.com/mermaid-js/mermaid
[httpyac]: https://github.com/anweber/httpyac
[hurl]: https://github.com/Orange-OpenSource/hurl
[Figma]: https://www.figma.com/
[Paket Mutfak]: https://www.paketmutfak.com.tr/
[@hasansezertasan]: https://github.com/hasansezertasan
[jdx]: https://github.com/jdx
[mise-docs]: https://mise.jdx.dev/
[astral-sh]: https://astral.sh/
[xc-gha]: https://github.com/marketplace/actions/run-xc
