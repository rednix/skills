---
name: ascii-chord
description: Show ASCII guitar chord diagrams using the ascii_chord CLI tool. Use when asked how to play a guitar chord, or to show chord charts/diagrams for any chord name (e.g. E, B7, Am, C, G, Dm, etc.). Requires git and cargo (Rust toolchain) to be installed.
---

# ascii-chord

Display ASCII guitar chord diagrams using [ascii_chord](https://github.com/yzhong52/ascii_chord) — an open-source Rust CLI by the same author as this skill.

## Required Tools

- **git** — to clone the repo
- **cargo / Rust** — to build and run the CLI
  - Check: `cargo --version`
  - Install if missing: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

## Setup

Check if already cloned; clone if not:

```bash
[ -d /tmp/ascii_chord ] || git clone https://github.com/yzhong52/ascii_chord /tmp/ascii_chord
```

No installation needed beyond that — `cargo run` builds and runs in one step.

## Usage

**Single chord:**
```bash
cd /tmp/ascii_chord && cargo run -- get <CHORD> 2>/dev/null
```

**Multiple chords side by side:**
```bash
cd /tmp/ascii_chord && cargo run -- list <CHORD1> <CHORD2> ... 2>/dev/null
```

**List all supported chords:**
```bash
cd /tmp/ascii_chord && cargo run -- all 2>/dev/null
```

## Examples

```bash
# Single chord
cargo run -- get Am

# Multiple side by side (great for progressions)
cargo run -- list C G Am F

# Full list of supported chord names
cargo run -- all
```

## Notes

- Suppress build warnings with `2>/dev/null`
- Chord names are case-sensitive (`Am` not `am`, `B7` not `b7`)
- After first build, subsequent runs are fast (binary is cached by cargo)
- Source repo: https://github.com/yzhong52/ascii_chord (MIT licensed)
