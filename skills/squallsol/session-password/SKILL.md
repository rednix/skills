# Session Password

**Version:** 1.1.0
**Author:** squallsol
**Price:** 9.9 USDT per call
**Platform:** [SkillPay](https://skillpay.me)

---

## Description (EN)

A secure passphrase authentication guard for OpenClaw sessions. Protects access with bcrypt-hashed passwords, security questions, and email recovery.

**Triggers:** When session starts, user mentions "口令", "password", "认证", "authentication", or similar authentication-related terms.

## 描述 (中文)

OpenClaw 会话的安全口令认证守护。使用 bcrypt 哈希口令、安全问题和邮箱恢复保护访问。

**触发条件：** 会话启动时，用户提及"口令"、"密码"、"认证"、"密码"等认证相关词汇。

---

## Pricing / 定价

| Plan | Price | Description |
|------|-------|-------------|
| **Buyout / 买断** | **$29 USDT** | One-time, lifetime access |
| **Per Call / 按次** | **$0.9 USDT** | Pay per use |

Billing is handled via [SkillPay](https://skillpay.me) (BNB Chain USDT).

- Users with buyout → No charge per call
- Users without buyout → $0.9 USDT per call
- Minimum deposit: 8 USDT

---

## Features / 功能特性

- ✅ bcrypt password hashing (cost factor 12) / bcrypt 口令哈希（成本因子 12）
- ✅ Configurable timeout (default 60 min) / 可配置超时（默认 60 分钟）
- ✅ Security question backup / 安全问题备用验证
- ✅ Email recovery system / 邮箱恢复系统
- ✅ Failed attempt lockout (5 attempts, 15 min) / 失败锁定（5 次，15 分钟）
- ✅ Bilingual support (zh-CN/en) / 中英双语支持
- ✅ Audit logging / 审计日志
- ✅ SkillPay billing integration / SkillPay 计费集成

---

## Setup / 安装设置

Run the setup wizard:
```bash
node skills/session-password/scripts/setup.js
```

运行设置向导：
```bash
node skills/session-password/scripts/setup.js
```

---

## Configuration Files / 配置文件

| File | Description |
|------|-------------|
| `memory/auth-config.json` | Main configuration / 主配置 |
| `memory/auth-users.json` | User credentials / 用户凭据 |
| `memory/auth-state.json` | Session state / 会话状态 |
| `memory/auth-audit.log` | Audit log / 审计日志 |

---

## Commands / 指令

| Chinese | English | Action |
|---------|---------|--------|
| 忘记口令 | forgot password | Trigger email recovery / 触发邮箱恢复 |
| 修改口令 | change password | Change passphrase / 修改口令 |
| 卸载口令skill | uninstall auth skill | Remove authentication / 移除认证 |

---

## Uninstall / 卸载

```bash
node skills/session-password/scripts/uninstall.js
```

---

## License

MIT
