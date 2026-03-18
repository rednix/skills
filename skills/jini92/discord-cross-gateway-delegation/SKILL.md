---
name: discord-cross-gateway-delegation
description: "Set up cross-gateway task delegation between two OpenClaw Discord bots using either a private server channel or a DM fallback. Use when: another OpenClaw bot lives on a different PC or a different Gateway and you want one bot to delegate tasks to the other. Triggers: 'delegate work to another OpenClaw bot', 'cross-gateway delegation', 'connect another gateway bot', 'Discord worker bot setup'. NOT for: same-gateway session routing, normal DM chat, or non-Discord automation."
---

# Discord Cross-Gateway Delegation

Set up delegation between two OpenClaw bots that run on different PCs and different gateways.

## Core rule

Treat the second bot as an **external worker**, not as an internal session.
Do **not** use same-gateway assumptions like `sessions_send` or local subagent routing.

## Default rollout

1. Create a **private Discord delegation lane**.
2. Invite the delegating bot into the target server.
3. Add the bot to the private channel and **save the permission change**.
4. Send a structured handshake task.
5. Test DM behavior and channel behavior separately.
6. If channel automation fails but DM works, switch to **DM fallback** until gateway config can be fixed.

## Required protocol

Use these message blocks:
- `[KAI_TASK]`
- `[KAI_STATUS]`
- `[KAI_DONE]`

Keep one task per message id / task id.

## What to do first

Read `references/setup-checklist.md` and follow it in order.
If the target bot is a secondary worker bot on another device, also read `references/macjini-rollout.md` for role split guidance.

## If channel messages fail

Read `references/diagnosis.md`.
If the worker bot responds in DM but not in server channels, first assume a guild-channel inbound policy issue.
For `groupPolicy: allowlist`, explicitly add the target guild/channel under `guilds`, then re-test channel-based `[KAI_STATUS]` before falling back.
