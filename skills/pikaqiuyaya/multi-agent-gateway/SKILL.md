# Multi-Agent Multi-Gateway 技能

> **多 Agent - 多网关 - 多机器人配置与管理技能**  
> 版本：1.0.1 | 最后更新：2026-03-18  
> 作者：pikaqiuyaya

---

## 📖 技能描述

本技能提供 OpenClaw 多 Agent 多网关架构的完整配置、管理和运维能力。支持：

- **多 Agent 部署** - 多智能体协同工作
- **多网关配置** - 独立端口、独立渠道、独立工作区
- **跨 Agent 通信** - 任务分发、状态同步、结果汇总
- **运维管理** - 服务启停、日志查看、故障排查
- **安全隔离** - 网络隔离、认证机制、数据隔离

---

## 🎯 适用场景

| 场景 | 说明 |
|------|------|
| 企业多角色部署 | 不同角色独立 Agent（如客服/运维/助理） |
| 渠道隔离 | 不同渠道绑定不同 Agent（飞书/微信/钉钉等） |
| 职责分离 | 不同职责明确分工（统筹/执行/运维） |
| 高可用架构 | 单点故障不影响其他 Agent 运行 |

---

## 🚀 快速开始

### 1. 查看当前部署

```bash
# 查看所有网关配置
ls -la ~/.openclaw/openclaw-*.json

# 查看所有网关服务
systemctl --user status openclaw-gateway-*.service

# 查看端口占用
netstat -tlnp | grep openclaw
```

### 2. 添加新 Agent

```bash
# 使用交互式向导
openclaw mg

# 填写信息：
# - 网关名称：new
# - 端口：19925
# - Workspace: workspace-new
# - 启用跨 Agent 通信：Y

# 说明：mg 向导会自动从 boss/ass/ops/main 复制配置（优先级：boss > ass > ops > main）
```

### 3. 绑定渠道（可选）

**使用 mg 向导时**：
```
请选择飞书配置 [1/2/3]:
  1) 使用新的飞书应用（推荐，每个网关独立）
  2) 使用和 main 相同的应用（共用应用）
  3) 跳过飞书配置（不绑定任何渠道，纯本地使用）← 选择 3 跳过
```

**选择 3 后**：
- ✅ 自动跳过后续所有飞书配置步骤
- ✅ 不生成飞书配置清单
- ✅ 不引导权限导入
- ✅ 不等待长连接建立
- ✅ 不添加事件订阅

**如果不需要连接任何渠道（纯本地使用）**：
- ✅ 可以跳过此步骤
- 网关正常运行，仅不接收外部消息
- 适合纯本地 API 调用或测试

**如果绑定飞书机器人**：
```bash
# 为新网关绑定飞书渠道
OPENCLAW_CONFIG_FILE=~/.openclaw/openclaw-agent-a.json openclaw channels login
```

**如果绑定其他渠道**：
- 微信、钉钉、QQ 等渠道请参考对应文档配置
- 或暂时跳过，后续再绑定

### 4. 配置跨 Agent 通信

在需要通信的 Agent 配置中添加：

```json
{
  "tools": {
    "sessions": { "visibility": "all" },
    "agentToAgent": { "enabled": true }
  }
}
```

### 5. 发送跨 Agent 消息

```javascript
// Agent-A → Agent-B
sessions_send({
  sessionKey: "agent:agent-b:feishu:direct:ou_xxx",
  message: "请检查服务状态",
  timeoutSeconds: 0
})

// Agent-A → Agent-C
sessions_send({
  sessionKey: "agent:agent-c:feishu:direct:ou_xxx",
  message: "请检查系统负载",
  timeoutSeconds: 60
})
```

---

## 📋 配置详解

### 网关配置结构

```json
{
  "agents": {
    "list": [{
      "id": "agent-a",
      "name": "Agent A",
      "workspace": "/home/admin/.openclaw/workspace-a"
    }],
    "defaults": {
      "model": { "primary": "dashscope-coding/qwen3.5-plus" },
      "maxConcurrent": 4
    }
  },
  "gateway": {
    "port": 19922,
    "auth": {
      "mode": "token",
      "token": "agent-a-token-19922"
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "dmPolicy": "open",
      "streaming": true
    }
  },
  "tools": {
    "sessions": { "visibility": "all" },
    "agentToAgent": { "enabled": true }
  }
}
```

### 关键配置项

| 配置 | 说明 | 推荐值 |
|------|------|--------|
| `gateway.port` | 网关端口 | 19922+ |
| `channels.feishu.dmPolicy` | 私聊策略 | open/pairing |
| `channels.feishu.streaming` | 流式输出 | true |
| `tools.sessions.visibility` | 会话可见性 | all (统筹 Agent) |
| `tools.agentToAgent.enabled` | 跨 Agent 通信 | true (统筹 Agent) |

---

## 🔄 典型工作流

### 任务分解模式

```
用户 → Agent-A: "检查所有服务"
     ↓
Agent-A → Agent-B: "检查文档服务"
Agent-A → Agent-C: "检查系统服务"
     ↓
Agent-B → Agent-A: "文档服务✓"
Agent-C → Agent-A: "系统服务✓"
     ↓
Agent-A → 用户：汇总报告
```

### 会话 Key 格式

```
agent:{agentId}:{channel}:{chatType}:{peerId}
```

**示例**:
- `agent:agent-b:feishu:direct:ou_xxx`
- `agent:agent-c:feishu:direct:ou_xxx`

---

## 🛠️ 运维命令

### 服务管理

```bash
# 启动/停止/重启
systemctl --user start openclaw-gateway-agent-a.service
systemctl --user stop openclaw-gateway-agent-a.service
systemctl --user restart openclaw-gateway-agent-a.service

# 批量操作
systemctl --user start openclaw-gateway-{agent-a,agent-b,agent-c}.service
```

### 日志查看

```bash
# 实时日志
journalctl --user -u openclaw-gateway-agent-a.service -f

# 最近 100 条
journalctl --user -u openclaw-gateway-agent-a.service -n 100
```

### 故障排查

```bash
# 检查端口
netstat -tlnp | grep openclaw

# 检查 OOM
dmesg | grep -i oom

# 验证配置
node -e "JSON.parse(require('fs').readFileSync('~/.openclaw/openclaw-agent-a.json'))"
```

---

## 📊 典型部署架构

| Agent | 端口 | Workspace | 用途 |
|-------|------|-----------|------|
| Agent-A | 19922 | workspace-a | 统筹协调 |
| Agent-B | 19923 | workspace-b | 执行助手 |
| Agent-C | 19930 | workspace-c | 运维专家 |

> 💡 **提示**: 实际部署时根据需求调整端口和 Agent 名称，每个网关需绑定独立的渠道应用。

---

## ⚠️ 注意事项

1. **端口唯一** - 每个网关必须使用不同端口
2. **Workspace 隔离** - 每个 Agent 独立工作区
3. **内存规划** - 建议网关数量不超过系统内存的 70%（单网关约 500-600MB）
4. **渠道可选** - 可以不绑定任何渠道（纯本地使用），或根据需要绑定飞书/微信/钉钉等

---

## 📚 相关文档

- 完整配置文档：`MULTI-AGENT-MULTI-GATEWAY.md`
- OpenClaw 官方文档：https://docs.openclaw.ai
- ClawHub 技能市场：https://clawhub.com

---

**技能版本**: 1.0.5  
**作者**: pikaqiuyaya  
**许可证**: MIT
