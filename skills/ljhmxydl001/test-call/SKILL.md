---
name: ruqi-mobility
description: 如祺出行 AI 助手。打车、叫车、查价、路线规划、订单管理时使用。支持：实时叫车/价格预估/订单查询/司机位置/路线规划/周边搜索。触发词："打车"、"叫车"、"去[地点]"、"查价格"、"路线规划"、"怎么走"、"取消订单"、"司机"、"查订单"。
homepage: https://testdocker-clientapi.ruqimobility.com
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": [] },
        "primaryEnv": "RUQI_CLIENT_MCP_TOKEN",
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "axios",
              "label": "Install axios (node)",
            },
          ],
      },
  }
---

# 如祺出行服务 (Ruqi Mobility)

通过 Ruqi MCP Server API 实现完整的出行服务，支持打车、路线规划等功能。

## 环境变量配置

**如果缺少 RUQI_CLIENT_MCP_TOKEN 或服务返回 400 错误，输出**：

> 您还没有配置 RUQI_CLIENT_MCP_TOKEN 环境变量，请配置环境变量或在 OpenClaw 配置文件中设置。

**环境变量：**

1. `RUQI_CLIENT_MCP_TOKEN` - MCP 认证令牌
2. `RUQI_CLIENT_ENV` - 当前环境，可选值："dev"、"test"、"uat"、"prod（默认）"

---

## 🚨 强制要求（必须遵守）

**每次 MCP 调用前必须执行以下步骤：**

1. **查阅 api_references.md 确认参数定义**
2. **严格遵循 API 文档中的参数名称和类型**

**重要约束：**

- ✅ 所有时间戳必须是**毫秒级**（13位数字）
- ✅ 城市编码必须是**6位数字字符串**，如 `440100`
- ✅ 经纬度必须是有效范围：纬度 -90~90，经度 -180~180
- ✅ 产品类型 prodType：`1`=实时订单，`2`=预约订单
- ✅ **create_ride_order 必须先调用 estimate_price**，获取 estimateId 后再调用

---

## 工作流程

### 0. 获取用户飞书标识

- 从消息上下文中获取当前用户的 `sender_id`(格式：`ou_xxx`)

### 1. 解析用户意图

根据用户消息内容判断操作类型，调用对应脚本。

#### 1.1 价格预估

- **触发词**：`多少钱`、`预估价格`、`从...到...`、`打车要多少钱`、`去XX要花多少`、`叫车费用`
- **前置条件**：必须先调用 `text_search` 获取 `startLat`、`startLng`、`endLat`、`endLng`
- **步骤**：
  - 提取起点终点坐标和地址。
  - 执行：
    ```bash
    node scripts/mcp_client.js estimate_price {{sender_id}} '{"startLat":23.118531,"startLng":113.332164,"endLat":23.128531,"endLng":113.342164,"startAddress":"广州市天河区天河路385号","endAddress":"广州市天河区珠江新城","fromCityCode":"440100","toCityCode":"440100","prodType":1,"expectStartTime":1710000000,"passengerPhone":"13800138000","scene":1,"sessionId":"session-123456","areaCode":"440106","channelDetailId":"channel-123","discountCode":"DISCOUNT123","multiRoute":true}'
    ```

#### 1.2 创建打车订单

- **触发词**：`帮我叫车`、`打车`、`叫车去XX`、`我要打车`、`预约用车`、`现在出发`
- **前置条件**：必须先调用 `estimate_price` 获取 `estimateId`
- **步骤**：
  - 确认已获取 `estimateId`。
  - 执行创建订单：
    ```bash
    node scripts/mcp_client.js create_ride_order {{sender_id}} '{"mobile":"18826139823","priorityContact":1,"expectStartTime":1773372869,"dispatchDuration":false,"submitLat":23.161564,"submitLng":113.473328,"submitAddress":"黄埔区PCI未来社区","submitAddDtl":"广东省广州市黄埔区新瑞路","fromLat":23.0957223,"fromLng":113.3341985,"fromAddress":"赤岗[地铁站]C1口","fromAddDtl":"赤岗[地铁站]C1口","fromCityCode":"440100","fromAdCode":"440105","fromCityName":"广州市","toLat":23.098126,"toLng":113.366218,"toAddress":"琶洲[地铁站]C口","toAddDtl":"琶洲[地铁站]C口","toCityCode":"440100","toAdCode":"440105","toCityName":"广州市","toPoiId":"2199035519762","prodType":"1","routeId":"5406931567564976608","multiRoute":true,"orderSource":0,"type":0,"estimateId":"7616578458997722382","sessionId":"1773371746004","transportCarList":[{"transportChannel":1,"supplierId":100,"carModelId":1}],"uncheckedTransportCarList":[],"orderPattern":1,"checkOrderTimeCloseTo":true}'
    ```
  - 创建订单成功后，从返回结果中提取 `orderId`。
  - **启动订单轮询**（后台异步执行，监控订单状态变化并推送消息）：
    ```bash
    node scripts/ruqi_poll_order.js {{orderId}} {{sender_id}} &
    ```

#### 1.2.1 订单轮询机制

订单创建成功后，系统会自动启动轮询监控订单状态：

- **轮询间隔**：每 5 秒查询一次
- **状态推送**：当订单状态变化时，自动向用户发送飞书消息通知
- **订单状态映射**：
  | 状态码 | 状态描述 |
  |--------|----------|
  | 3 | 指派中 |
  | 4 | 已接单 |
  | 5 | 已发车 |
  | 6 | 已到达 |
  | 7 | 服务中 |
  | 8 | 服务已结束 |
  | 9 | 已完成 |
  | 10 | 已取消 |
  | 17 | 免密待支付 |
  | 18 | 待支付 |
- **终止条件**：订单进入终态（已完成/已取消/待支付）后自动停止轮询

#### 1.3 查询打车订单

- **触发词**：`查询订单`、`订单状态`、`我的订单怎么样了`、`司机到了吗`、`订单详情`
- **步骤**：
  - 提取订单ID。
  - 执行：
    ```bash
    node scripts/mcp_client.js query_ride_order {{sender_id}} '{"orderId":"ORDER123456"}'
    ```
- **特殊处理**：当返回 `orderState = 18`（待支付状态）时，提示用户：
  > 司机已到达目的地，当前订单已结束，麻烦到如祺出行APP支付这笔订单。欢迎下次再次乘车，谢谢！

#### 1.4 查询订单列表

- **触发词**：`我的订单`、`历史订单`、`订单记录`、`查看所有订单`、`待支付订单`、`待评价订单`
- **步骤**：
  - 确定查询类型（全部/待支付/待评价/未完成）。
  - 执行：
    ```bash
    node scripts/mcp_client.js query_order_list {{sender_id}} '{"pageIndex":1,"pageSize":10,"type":"1"}'
    ```
- **type 参数说明**：`1`=全部、`2`=待支付、`3`=待评价、`4`=未完成、`5`=发票列表

#### 1.5 取消订单

- **触发词**：`取消订单`、`不想坐了`、`取消打车`、`不要这单了`
- **步骤**：
  - 提取订单ID。
  - 执行：
    ```bash
    node scripts/mcp_client.js cancel_order {{sender_id}} '{"orderId":"ORDER123456"}'
    ```

#### 1.6 获取司机位置

- **触发词**：`司机在哪`、`司机位置`、`司机到哪了`、`司机还有多远`
- **步骤**：
  - 提取订单ID。
  - 执行：
    ```bash
    node scripts/mcp_client.js get_driver_location {{sender_id}} '{"orderId":"ORDER123456"}'
    ```

#### 1.7 文本搜索

- **触发词**：`搜索XX`、`查找XX`、`找一下XX`、`帮我找XX`
- **步骤**：
  - 提取搜索关键词和城市信息。
  - 执行：
    ```bash
    node scripts/mcp_client.js text_search {{sender_id}} '{"keyword":"天河城","region":"广州","cityCode":"440100"}'
    ```

#### 1.8 周边检索

- **触发词**：`附近有什么`、`周边有什么`、`附近有XX吗`、`周围有什么`、`这附近有什么好吃的`
- **步骤**：
  - 提取用户当前位置。
  - 执行：
    ```bash
    node scripts/mcp_client.js nearby_search {{sender_id}} '{"latitude":23.118531,"longitude":113.332164,"radius":1000}'
    ```

#### 1.9 逆地理编码

- **触发词**：`这个位置在哪`、`经纬度转地址`、`这个坐标是什么地方`、`定位在哪`
- **步骤**：
  - 提取用户提供的经纬度。
  - 执行：
    ```bash
    node scripts/mcp_client.js reverse_geocode {{sender_id}} '{"lat":23.118531,"lng":113.332164,"getPoi":1}'
    ```

#### 1.10 驾车路径规划

- **触发词**：`从A到B怎么走`、`规划路线`、`怎么去XX`、`导航到XX`、`开车去XX怎么走`
- **步骤**：
  - 提取起点终点坐标。
  - 执行：
    ```bash
    node scripts/mcp_client.js driving_route_planning {{sender_id}} '{"startLat":23.118531,"startLng":113.332164,"endLat":23.128531,"endLng":113.342164,"policy":3,"preferencePolicy":1}'
    ```
- **policy 参数说明**：`1`=参考实时路况/时间最短、`2`=网约车场景-接乘客、`3`=网约车场景-送乘客
- **preferencePolicy 参数说明**：`1`=参考实时路况、`2`=少收费、`3`=不走高速、`4`=使用地点出入口作为目的地

#### 1.11 获取推荐上车点

- **触发词**：`哪里上车`、`推荐上车点`、`在哪等车`、`最近的上车点`
- **步骤**：
  - 提取用户当前位置坐标。
  - 执行：
    ```bash
    node scripts/mcp_client.js get_recommended_boarding_point {{sender_id}} '{"lat":23.118531,"lng":113.332164}'
    ```

## 用户确认流程

- **实时单**：需要用户确认
- **预约单**：直接创建订单，无需确认
- **取消订单**：需要用户确认

### 实时单确认流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户发起打车请求                             │
│               "我要从天河去珠江新城"                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 地址解析 (text_search/nearby_search)                   │
│  - 解析起点：天河 → (113.332, 23.118)                          │
│  - 解析终点：珠江新城 → (113.342, 23.128)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 价格预估 (estimate_price)                               │
│  - 获取预估ID和价格                                             │
│  - 展示给用户                                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ Step 3: 用户确认                                           │
│  - 询问用户："确认下单吗？"                                     │
│  - 等待用户明确回复（如"确认"、"下单"等）                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: 创建订单 (create_ride_order)                            │
│  - 使用 estimate_price 返回的 estimateId                        │
│  - 返回: orderId, phoneNumberSuffix                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 订单状态跟踪 (query_ride_order 轮询)                   │
│  - 自动进入轮询模式                                             │
│  - orderState <= 8 时持续轮询                                   │
│  - orderState > 8 时退出轮询                                    │
└─────────────────────────────────────────────────────────────────┘
```

---
