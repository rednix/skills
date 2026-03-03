---
name: jun-invest-option-master-installer
description: "Installer skill: via chat, install/upgrade & register the jun-invest-option-master isolated agent (no manual steps)."
---

# jun-invest-option-master-installer

目标：你只需要在聊天里说一句，我就会按固定步骤把 **agent：`jun-invest-option-master`** 安装/升级到可用状态（不含 channel 绑定）。

## 对话口令（推荐）
- **“安装/升级 jun-invest-option-master（不绑定channel）”**

## 固定步骤（由我自动执行）
1) `clawhub install/update jun-invest-option-master-installer`
2) 同步资产到独立 workspace：`/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master`
3) 注册 isolated agent：`openclaw agents add jun-invest-option-master --non-interactive --workspace ...`
4) 需要时重启 gateway（通常不强制）

##（可选）命令行一键
```bash
bash scripts/auto-install.sh
```

说明：本 skill 不包含任何 secrets/token；绑定 bot/channel 另行处理。
