---
name: skills-coze-jiadian
description: 收费技能示例 - 授权验证 + 手机号绑定 skills-coze-jiadian
license: MIT
---

# skills-coze-jiadian

收费技能示例，演示如何在 ClawHub 发布带授权验证和手机号绑定的付费技能。


# Installation

clawhub install skills-coze-jiadian

## 隐私说明

**本技能是付费技能演示，需要绑定手机号才能使用。**

本技能会：
1. **收集手机号** - 需要用户输入手机号进行绑定
2. **发送到后端** - 手机号会通过 HTTPS POST 发送到第三方服务器 `https://yunji.focus-jd.cn/api/skill/lin/test` 进行注册验证
3. **本地存储** - 绑定成功后，手机号会**使用授权码作为密钥加密存储**在技能目录下的 `.phone.json` 文件中，方便下次直接使用

**⚠️ 重要提示：使用本技能即表示你同意将手机号发送到上述第三方域名。请确保你信任该域名和技能作者后再使用。**

## 配置

### 必需环境变量

```bash
export SKILL_LICENSE_KEY=你的授权码
```

购买授权码请访问：https://your-website.com/buy

## When to use

- 用户触发付费技能
- 需要授权验证 + 手机号绑定
- 授权通过后保存手机号，下次直接使用

## Instructions

1. 用户触发技能
2. 打印欢迎信息
3. 检查 `SKILL_LICENSE_KEY` 授权 → 授权失败提示购买并退出
4. 授权通过后，检查本地是否已有手机号 → 有直接使用，没有提示输入
5. 发送手机号到后端 → 成功保存，失败提示

## Parameters

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 否 | 测试消息 |