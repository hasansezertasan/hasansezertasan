---
date:
  created: 2026-06-24
  updated: 2026-06-24
categories:
  - python
  - agentic-coding
  - open-source
authors:
  - hasansezertasan
slug: the-story-behind-keycast
---

# The story behind keycast, a tool I built but never needed

I've been writing Python for more than five years now: open source, freelance, full-time, contract work. It's a versatile language, and the ecosystem around it keeps reinforcing that. At some point you start to believe you can build almost anything with it.

Early on I had a question in the back of my head: *how far can I actually get with Python?* The question eventually faded, but I never fully let it go. Every so often I pick it back up and put it to the test. This post is about one of those tests.

<!-- more -->

## The overlay I kept noticing in tutorials

I stopped watching tutorials as often a few years ago, but back when I did, one detail in some of them always caught my eye: a small, semi-transparent black window on screen showing the presenter's keystrokes. You could see exactly what they pressed, usually which shortcut, and finally connect the "wait, how did they do that?" moment to an actual key combo.

When I looked into it, I found tools like KeyCastr, Keyviz, and Keystroke Pro.

Naturally, I asked myself: *could I build this in Python?* That was three or four years ago, and I answered it back then. I read up, compared the libraries, and the conclusion was clear. Yes, I could. So I... didn't. I'd learned what I wanted to learn and the curiosity was satisfied. The thing itself was never the point.

## Same question, different toolbox

Last year, while digging through my old research notes, that question resurfaced. But the context had completely changed.

My own tooling had moved from GitHub Copilot to Cursor, which was *the* big thing at the time (Claude Code wasn't on my radar yet). So the question quietly mutated into a new one: *can I build this with Cursor?* I figured I'd pick up a few things along the way, and honestly, there's something satisfying about getting an LLM to darn your own socks for once. So I built keycast through an agentic workflow.

A year passed. Both the tools and the workflows got noticeably better, and Claude Code became where I parked. The itch came back, and I wanted to run the experiment one more time with sharper tools, this time properly in the AI era.

## keycast, today

This week, again working through AI agents, I shipped it properly, both as a package and as a Homebrew formula. It's a cross-platform keystroke and mouse-click visualizer written in Python, the same semi-transparent overlay I'd noticed in those tutorials. Under the hood it's `pynput` for capturing input, a Tkinter overlay for the on-screen window, `pydantic-settings` for config, and `typer` for the CLI, all on Python 3.14.

To be clear, I don't actually need keycast, and I never did. I wasn't scratching a personal itch for the tool itself. The point was always the journey: deepening my understanding of Python and its ecosystem, and seeing how far I could push a real project with each new generation of tooling. keycast is just the artifact that fell out of that experiment.

You can try it in one line:

```bash
uvx keycast
```

It runs on macOS, Linux, and Windows, fades events out after a configurable delay, and reads a JSON config from `~/.keycast/config.json` that it creates for you on first run.

If you give it a spin, I'd genuinely love to hear what you think. And if you like it, a star goes a long way :star_struck:

:point_right: <https://github.com/hasansezertasan/keycast>
