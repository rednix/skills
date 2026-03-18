# Install

## Local install

```bash
cp -R skills/gougoubi-recovery-ops "$CODEX_HOME/skills/"
```

## GitHub install

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path skills/gougoubi-recovery-ops
```

## Verify

```bash
ls -la "$CODEX_HOME/skills/gougoubi-recovery-ops"
```

Restart the agent runtime after installation.
