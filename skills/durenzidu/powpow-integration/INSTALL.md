# PowPow Integration Skill - 安装指南

## 📦 文件包内容

本文件包包含可直接部署到 OpenClaw 的 PowPow 集成 Skill。

## 📁 文件结构

```
powpow-skill-upload-v1.1.0/
├── dist/                       # 编译后的代码
│   ├── index.js               # 主入口文件
│   ├── index.d.ts             # TypeScript 类型定义
│   ├── powpow-client.js       # PowPow API 客户端
│   └── utils/                 # 工具函数
│       ├── constants.js
│       ├── rate-limiter.js
│       └── validator.js
├── skill.json                 # Skill 配置文件
├── package.json               # NPM 包配置
├── README.md                  # 使用说明
└── INSTALL.md                 # 本文件
```

## 🚀 安装步骤

### 1. 上传到 OpenClaw

将本文件夹压缩为 zip 文件，然后上传到 OpenClaw Skill 管理界面。

### 2. 配置 Skill

在 OpenClaw 配置界面设置以下参数：

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

### 3. 验证安装

安装完成后，执行以下命令测试：

```
register    # 注册 PowPow 账号
login       # 登录 PowPow
listDigitalHumans  # 列出数字人
```

## ⚙️ 配置说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `powpowBaseUrl` | string | 否 | `https://global.powpow.online` | PowPow API 基础 URL |
| `powpowApiKey` | string | 否 | - | PowPow API 密钥（可选） |
| `defaultLocation` | object | 否 | 北京坐标 | 数字人默认位置 |

## 📝 版本信息

- **版本**: v1.1.0
- **更新日期**: 2026-03-17
- **API 端点**: `https://global.powpow.online`

## 🔧 故障排除

### 问题 1：无法连接到 API

**症状**: 命令执行失败，提示连接错误

**解决**:
1. 检查 `powpowBaseUrl` 配置是否正确
2. 确认网络可以访问 `https://global.powpow.online`
3. 测试 API: `curl https://global.powpow.online/api/openclaw/robots`

### 问题 2：认证失败

**症状**: 登录或注册失败

**解决**:
1. 确认用户名和密码正确
2. 检查 API 服务是否正常运行
3. 查看 OpenClaw 日志获取详细错误信息

## 📞 支持

如有问题，请联系开发团队或查看 README.md 获取更多信息。
