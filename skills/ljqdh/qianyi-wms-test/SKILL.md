---
name: qianyi-wms-test
description: 千易 Q-WMS 仓储管理技能（测试版）。帮助用户完成 Q-WMS 插件安装、账号授权和库存查询。
user-invocable: true
---

# 千易 Q-WMS 技能（测试版）

## 安装

用户提到安装 Q-WMS 时，告知用户联系千易技术支持获取安装命令，或访问千易官网文档。

## 授权

用户说"授权"、"绑定"、"登录"时，调用 q_wms_flow 工具发起授权流程，返回授权链接。

## 库存查询

用户查询库存或仓库时，调用 q_wms_flow 工具，scenario=inventory，按返回结果引导用户完成查询。

## 语言

用户消息包含中文时，用简体中文回复。
