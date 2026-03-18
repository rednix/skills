# Diagnosis

## Known-good findings from this setup pattern

The following symptoms mean different things:

### Symptom: controller bot cannot send to the channel
Likely causes:
- bot not invited to server
- bot not added to private channel
- permission modal change not saved

### Symptom: worker can see the private channel but never auto-replies
Likely causes:
- worker bot treats guild channels differently from DMs
- worker gateway inbound policy blocks server-channel input
- worker allowlist/guild filtering excludes this server/channel
- worker is configured as DM-first only

### Symptom: worker responds in DM but not in the private channel
This is the most important diagnostic split.
It means:
- the bot is alive
- Discord token/gateway are fine
- inbound works at least in DM
- the remaining issue is almost certainly **guild/server-channel inbound policy**

## Most likely config areas to inspect on the worker gateway

Priority order:
1. `groupPolicy`
2. `allowFrom`
3. `guilds`
4. `inboundWorker`

Check both account-scoped and global Discord config paths when relevant:
- `channels.discord.accounts.default.groupPolicy`
- `channels.discord.accounts.default.allowFrom`
- `channels.discord.accounts.default.guilds`
- `channels.discord.accounts.default.inboundWorker`
- `channels.discord.groupPolicy`
- `channels.discord.allowFrom`
- `channels.discord.guilds`
- `channels.discord.inboundWorker`

## Recommended temporary fallback

If the worker bot replies in DM but not in guild channels:
- do not block the project on config work
- switch to **DM-based delegation** immediately
- keep the structured task protocol unchanged
- revisit guild-channel config later when the worker machine is reachable
