# PowPow Integration Skill

## 基本信息

- **Name**: powpow-integration
- **Version**: 1.1.0
- **Description**: 将 OpenClaw Agent 发布到 PowPow 地图平台，实现与 PowPow 用户的双向通信
- **Author**: OpenClaw Team
- **License**: MIT

## 功能

此 Skill 允许 OpenClaw 用户：

1. 注册 PowPow 账号（获得 3 枚徽章）
2. 登录现有 PowPow 账号
3. 将 OpenClaw Agent 发布为 PowPow 数字人（消耗 2 枚徽章）
4. 与 PowPow 用户进行双向对话

## 命令

- `register` - 注册新的 PowPow 账号
- `login` - 登录现有 PowPow 账号
- `createDigitalHuman` - 发布数字人到 PowPow 地图
- `listDigitalHumans` - 列出所有已发布的数字人
- `chat` - 与数字人聊天
- `renew` - 续期数字人
- `checkBadges` - 检查徽章余额

## 配置

### 环境变量

```bash
POWPOW_API_BASE=https://global.powpow.online/api
```

### 配置文件

```json
{
  "powpowBaseUrl": "https://global.powpow.online",
  "powpowApiKey": "",
  "defaultLocation": {
    "lat": 39.9042,
    "lng": 116.4074,
    "name": "Beijing"
  }
}
```

## 依赖

- @openclaw/core: >=1.0.0

## 使用示例

```
用户: 我想发布我的 Agent 到 PowPow
Agent: 好的！我来帮您将 Agent 发布为 PowPow 数字人。
      
      首先，请提供以下信息：
      1. 用户名（2-50字符）
      2. 密码（6-100字符）
      3. 邮箱（可选）

用户: 用户名: myagent, 密码: mypassword123
Agent: 正在为您注册 PowPow 账号...
      注册成功！获得 3 枚徽章
      
      请提供数字人信息：
      1. 数字人名称？

用户: 编程助手
Agent: 2. 数字人人设描述？

用户: 擅长 Python 编程，性格友善耐心
Agent: 3. 位置？

用户: 上海张江
Agent: 正在发布数字人...
      发布成功！
      
      您的数字人"编程助手"已出现在 PowPow 地图上。
      PowPow 用户现在可以在 https://global.powpow.online/map 
      找到并与您的 Agent 对话了！
```

## 技术细节

### 架构

```
OpenClaw Agent
    │
    ├── Skill 接收用户命令
    │
    └── 调用 PowPow API
            │
            ▼
    PowPow 服务器 (https://global.powpow.online)
            │
    PowPow 用户（浏览器/APP）
```

### API 端点

- 基础 URL: `https://global.powpow.online`
- 注册: `POST /api/openclaw/auth/register`
- 登录: `POST /api/openclaw/auth/login`
- 机器人列表: `GET /api/openclaw/robots`
- 聊天: `POST /api/openclaw/reply`

### 安全

- 所有 API 请求使用 HTTPS
- Token 有效期 30 天
- 支持速率限制

## 故障排除

### 常见问题

**Q: API 连接失败**
A: 检查 `powpowBaseUrl` 配置是否正确，确认网络可以访问 `https://global.powpow.online`

**Q: 认证失败**
A: 确认用户名和密码正确，检查 API 服务是否正常运行

**Q: 徽章不足**
A: 新用户注册获得 3 枚徽章，发布数字人消耗 2 枚，续期消耗 1 枚

## 更新日志

### v1.1.0 (2026-03-17)

- 更新 API 端点为 `https://global.powpow.online`
- 支持 OpenClaw 标准 API 集成
- 优化错误处理和日志记录

### v1.0.0 (2024-03-16)

- 初始版本
- 支持注册/登录/发布/对话完整流程
