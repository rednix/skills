---
name: memoryai
description: "Persistent long-term memory via MemoryAI server. Store, recall, and manage context across sessions."
metadata: {"openclaw": {"always": true, "emoji": "🧠"}}
---

# MemoryAI

Cloud memory system for AI agents. Server-backed PostgreSQL + pgvector + Neural Graph.
Zero dependencies — uses only Python stdlib (urllib).

## Setup

1. Get API key from your MemoryAI server
2. Edit `{baseDir}/config.json`:
```json
{
  "endpoint": "https://your-memoryai-server.com",
  "api_key": "hm_sk_your_key_here"
}
```

## Commands

### Store memory
```bash
python {baseDir}/scripts/client.py store -c "data to remember" -t "tag1,tag2" -p hot
```
Priority: `hot` (important, frequent recall) | `warm` (default) | `cold` (archive)

Optional parameters:
- `--memory-type <type>` — Classify the memory: `fact`, `decision`, `preference`, `error`, `goal`, `episodic`
- `--retention <policy>` — Control lifespan: `forever`, `6m`, `1y`, `auto` (default)

Examples:
```bash
# Store a decision that should never be deleted
python {baseDir}/scripts/client.py store -c "Use PostgreSQL for all new services" -t "architecture" -p hot --memory-type decision --retention forever

# Store a preference with 1-year retention
python {baseDir}/scripts/client.py store -c "User prefers dark mode" -t "preferences" --memory-type preference --retention 1y

# Store an error lesson (auto decay)
python {baseDir}/scripts/client.py store -c "Never use rm -rf on mounted volumes" -t "errors" -p hot --memory-type error
```

### Recall memory
```bash
python {baseDir}/scripts/client.py recall -q "what was discussed?" -d deep
```
Depth: `fast` (quick lookup) | `deep` (semantic + graph) | `exhaustive` (full scan)

Optional: `--memory-type <type>` — Filter results by memory type.
```bash
# Recall only decisions
python {baseDir}/scripts/client.py recall -q "database choices" --memory-type decision

# Recall only preferences
python {baseDir}/scripts/client.py recall -q "user settings" --memory-type preference
```

### Stats
```bash
python {baseDir}/scripts/client.py stats
```

### Compact (compress context into memory)
```bash
python {baseDir}/scripts/client.py compact -c "session transcript or context" -t "task description"
```

### Restore context
```bash
python {baseDir}/scripts/client.py restore -t "what I was working on"
```

### Check context health
```bash
python {baseDir}/scripts/client.py check
```
Returns `urgency`: `low` | `medium` | `high` | `critical`

### Reflect (auto-reflection)
```bash
python {baseDir}/scripts/client.py reflect --hours 24 --max-insights 5
```
Scans recent chunks, finds recurring patterns (tags, memory types), and creates insight chunks automatically.

## QF Features (v0.5.0)

### Memory Types
Classify memories for better organization and filtering:
| Type | Use for |
|------|---------|
| `fact` | Objective information, data points |
| `decision` | Technical/architectural decisions |
| `preference` | User preferences, settings |
| `error` | Bugs, lessons learned |
| `goal` | Objectives, targets |
| `episodic` | Events, conversations, experiences |

All types are optional — omit for general-purpose memories.

### Retention Policy
Control how long memories live:
| Policy | Behavior |
|--------|----------|
| `forever` | Never deleted or decayed. Inviolable. |
| `6m` | Auto-expires after 6 months |
| `1y` | Auto-expires after 1 year |
| `auto` | Subject to Ebbinghaus decay (default) |

Use `forever` for critical decisions, API keys, architecture choices. Use `auto` for day-to-day context.

### Contradiction Detection
When storing a new memory, the engine automatically checks for contradictions with existing memories. If a conflict is found, the response includes:
- `contradiction_warning`: description of the conflict
- `contradicts`: list of conflicting chunk IDs

No action needed — just be aware that the store response may flag conflicts.

### Spreading Activation
Recall now follows edges between related chunks. Chunks linked by shared tags or entities are connected via a neural graph. BFS traversal from top results finds associatively related memories. This is transparent — recall just returns smarter results.

### Hebbian Learning
Memory connections strengthen with use. When chunks are co-recalled together, their edge weights increase by 0.1 per co-recall (capped at 5.0). Frequently associated memories become more tightly linked over time. Transparent to the user.

### Memory Decay + Consolidation
Automatic lifecycle management using Ebbinghaus-style decay:
- Only affects `retention=auto` chunks
- `forever`, `6m`, `1y` chunks are inviolable — never decayed
- Unused memories gradually lose strength
- Recalled memories get reinforced (see Hebbian Learning)

### Auto-Reflection
Generate insights from patterns in recent memories:
```bash
python {baseDir}/scripts/client.py reflect --hours 24 --max-insights 5
```
- Scans chunks from the last N hours
- Identifies recurring tags, memory types, content types
- Creates insight chunks tagged `[insight, auto-reflection]`
- Useful for periodic self-review or heartbeat tasks

## Context Guard (Auto-Setup)

On first use, create a cron job to automatically monitor and compact memory when needed.

- Name: `context-guard`
- Schedule: every 20 minutes (`everyMs: 1200000`)
- Session: `isolated`
- Delivery: `none`
- Payload (agentTurn):
```
Run context check: python {baseDir}/scripts/client.py check
If urgency is 'high' or 'critical': run python {baseDir}/scripts/client.py compact -c "auto context guard backup" -t "context-guard"
Reply NO_REPLY.
```

## When to Use

| Trigger | Action | Priority | Tags | memory_type | retention |
|---------|--------|----------|------|-------------|-----------|
| Task completed | store outcome | hot | projects | fact | auto |
| User says "remember this" | store content | hot | people | — | forever |
| Research/search done | store findings | warm | research | fact | auto |
| Technical decision | store decision | hot | decisions | decision | forever |
| Error/lesson learned | store lesson | hot | errors | error | forever |
| User preference noted | store preference | warm | preferences | preference | 1y |
| Goal/objective set | store goal | hot | goals | goal | 1y |
| Need past context | recall first | — | — | — | — |
| End of session | compact context | — | — | — | — |
| Start of session | restore context | — | — | — | — |
| Periodic review | reflect | — | — | — | — |

## Rules

- Always recall before answering questions about past work
- Store important outcomes after completing tasks
- Do not expose memory system internals to the user
- Present recalled information naturally, as if you simply "remember" it
- Context guard runs silently — never notify the user about compaction
- Use `--memory-type` when the type is clear; omit when ambiguous
- Use `--retention forever` for critical decisions and user-stated preferences
- Contradiction warnings in store responses should be noted but don't block storage

## Data & Privacy

This skill sends stored memories to the configured MemoryAI endpoint via HTTPS.
All data is transmitted over encrypted connections and stored in isolated, private databases.
Users can export all data via `/v1/export` and delete all data via `DELETE /v1/data` at any time.
