---
name: catchclaw
description: "Search, install, and export agentars from the CatchClaw marketplace. Use when the user wants to find, install, or package agent templates."
user-invocable: true
---

# CatchClaw Agentar Manager

An agentar is a distributable agent archive (ZIP) containing workspace files such as SOUL.md, skills, and other configuration. It can be installed as a new agent or used to overwrite an existing agent.

## Trigger Conditions

- User asks to search / find / browse agentars
- User asks to install / download a specific agentar
- User asks to export / package the current agent as an agentar
- User mentions the keyword "agentar" or "catchclaw"

## CLI Location

Before running any command, locate the CLI using this priority:

1. **Primary:** `node ~/.agents/skills/catchclaw/agentar_cli.mjs`
2. **Fallback:** `agentar` (if installed standalone and available in PATH)

Verify the primary path exists first. If neither is found, instruct the user to reinstall the skill from CatchClaw.

All commands below use `$CLI` as shorthand for the resolved CLI invocation.

## Commands

### Search

```bash
$CLI search <keyword>
```

Search the CatchClaw marketplace for agentars matching the keyword.

### List

```bash
$CLI list
```

List all available agentars in the marketplace.

### Install

```bash
$CLI install <slug> --overwrite
$CLI install <slug> --name <name> [--api-key <key>]
```

Install an agentar from the marketplace.

**Options:**
- `--overwrite` — Overwrite the main agent (`~/.openclaw/workspace`). Existing workspace is backed up automatically.
- `--name <name>` — Create a new agent with the given name. Existing agents are not affected.
- `--api-key <key>` — (Optional) API key to save into `skills/.credentials` for agentars that require backend authentication.

### Export

```bash
$CLI export [--agent <id>] [-o <path>] [--include-memory]
```

Export an agent as a distributable agentar ZIP package.

**Options:**
- `--agent <id>` — Agent ID to export. If omitted, all agents are listed for interactive selection.
- `-o, --output <path>` — Output ZIP file path (default: `./<agent-id>.zip`).
- `--include-memory` — Include MEMORY.md in export (excluded by default).

### Version

```bash
$CLI version
```

Show the CLI version.

## Installation Rules

<HARD-GATE>
Before executing `install`, you MUST first confirm the installation mode with the user. Do NOT run the install command without the user's explicit choice.

Present the following two options:
1. **overwrite** — Overwrite the main agent (~/.openclaw/workspace). The existing workspace will be backed up automatically.
2. **new** — Create a new agent. The existing agents are not affected.

After the user selects overwrite, execute: `$CLI install <slug> --overwrite`
After the user selects new, execute: `$CLI install <slug> --name <user-specified name>`

If the user does not specify a name, use the slug as the default name.

Never execute install without the user's explicit mode selection.
</HARD-GATE>

## Export Rules

- MEMORY.md is excluded by default. Only include it if the user explicitly requests it with `--include-memory`.
- After a successful export, remind the user to review the exported ZIP for any sensitive data (API keys, credentials, personal information).
- Export is a purely local operation — it does not require network access.

## Error Handling

| Error | Action |
|-------|--------|
| CLI file not found at either path | Instruct user to reinstall the skill from CatchClaw marketplace |
| API unreachable or network error | Suggest checking network connectivity, or override the API URL with: `export AGENTAR_API_BASE_URL=<url>` |
| Node.js not installed | Instruct user to install Node.js from https://nodejs.org/ |
| Download or extraction failure | Show the error message and suggest retrying the command |

## Workflow

1. **Search**: Run `$CLI search <keyword>` to find agentars. Each result includes a slug identifier.
2. **Install**: Confirm installation mode with the user first (HARD-GATE). Then execute the install command with the chosen mode.
3. **Export**: Run `$CLI export`. When `--agent` is omitted, all agents are listed for selection. After the user selects an agent, run again with `--agent <id>`.
