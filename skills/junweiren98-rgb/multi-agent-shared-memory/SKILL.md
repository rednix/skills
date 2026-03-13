---
name: shared-memory
description: Set up shared memory between multiple OpenClaw agents so they stay in sync without the user repeating context. Use when a user has 2+ agents (workspaces) and wants them to share knowledge, sync conversation summaries, and maintain a common long-term memory. Triggers on phrases like "shared memory", "agent sync", "multi-agent memory", "agents share context", "stop repeating myself to different agents".
---

# Shared Memory for Multi-Agent OpenClaw

Enable multiple OpenClaw agents to share knowledge, conversation context, and long-term memory through a shared directory structure and sync protocol.

## Problem

When you run multiple OpenClaw agents (e.g. a main assistant + a specialist), each agent wakes up fresh every session with no knowledge of what the other discussed with you. You become the "messenger" repeating the same context to each agent.

## Solution Overview

A `shared-knowledge/` directory lives inside one agent's workspace and is accessible to all participating agents. Each agent:
1. **Reads** the shared memory at session start
2. **Updates** their own sync file at session end
3. **Contributes** to a shared long-term memory when important decisions happen

## Setup

### Step 1: Create the shared directory

Pick one workspace as the host (typically the primary agent). Create the structure:

```
shared-knowledge/
├── SHARED-MEMORY.md          # Shared long-term memory
├── README.md                 # Usage rules (optional)
├── sync/                     # Per-agent conversation summaries
│   ├── agent-a-latest.md     # Agent A's latest summary
│   └── agent-b-latest.md     # Agent B's latest summary
└── projects/                 # Shared project documents (optional)
```

Use the templates in `assets/` to scaffold these files:

```bash
# From the skill directory:
cp assets/SHARED-MEMORY.template.md  <workspace>/shared-knowledge/SHARED-MEMORY.md
cp assets/README.template.md         <workspace>/shared-knowledge/README.md
cp assets/sync-latest.template.md    <workspace>/shared-knowledge/sync/<agent-name>-latest.md
```

Replace placeholders (`{{AGENT_A_NAME}}`, `{{AGENT_B_NAME}}`, etc.) with actual agent names/emoji.

### Step 2: Configure each agent's AGENTS.md

Add the shared memory protocol to each participating agent's `AGENTS.md`. See `references/agents-protocol-snippet.md` for the exact block to insert.

Key additions per agent:
- **Session start**: Read `SHARED-MEMORY.md` + the *other* agent's sync file
- **Session end**: Update *own* sync file with conversation highlights
- **On important info**: Update `SHARED-MEMORY.md`

### Step 3: Ensure file access

Both agents need read/write access to the `shared-knowledge/` directory:

- **Same machine, different workspaces**: Use a symlink or absolute path reference in AGENTS.md
- **Same machine, nested workspaces**: If workspace-b is inside the same `.openclaw/` directory, use relative paths

Example symlink (Windows):
```powershell
New-Item -ItemType SymbolicLink -Path "<workspace-b>\shared-knowledge" -Target "<workspace-a>\shared-knowledge"
```

Example symlink (Linux/Mac):
```bash
ln -s <workspace-a>/shared-knowledge <workspace-b>/shared-knowledge
```

## Protocol Rules

### What goes in shared memory
- ✅ User info, preferences, decisions
- ✅ Project context and progress
- ✅ Conversation summaries (each agent's sync file)
- ✅ Shared reference documents

### What stays private
- ❌ Agent personality files (SOUL.md, IDENTITY.md)
- ❌ Private memories and persona settings
- ❌ Credentials, tokens, passwords

### Sync cadence
| Trigger | Action |
|---------|--------|
| Session start | Read `SHARED-MEMORY.md` + other agents' sync files |
| Session end | Update own sync file with conversation highlights |
| Important decision | Update `SHARED-MEMORY.md` |

## Customization

- **More than 2 agents**: Add one sync file per agent in `sync/`. Each agent reads all *other* agents' files.
- **Project-specific docs**: Use `projects/` subdirectory for shared project documentation.
- **Selective sharing**: Agents can be configured to only read (not write) shared memory if they are read-only participants.
