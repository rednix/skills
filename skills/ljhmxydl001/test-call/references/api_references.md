## 工具参数定义（必须严格遵循）

## 基础参数说明

所有工具调用都需要以下基础参数（从BaseRequest继承）：

| 参数名       | 类型    | 必需 | 说明                                                                         |
| ------------ | ------- | ---- | ---------------------------------------------------------------------------- |
| `platform`   | string  | ✅   | 平台：Android、iOS、MiniProgram_Android、MiniProgram_iOS、H5_Android、H5_iOS |
| `deviceId`   | string  | ✅   | 设备唯一标识                                                                 |
| `deviceType` | string  | ✅   | 设备型号                                                                     |
| `timestamp`  | integer | ✅   | 毫秒级时间戳                                                                 |
| `tdBlackBox` | string  | ⚠️   | 大部分接口必需                                                               |
| `token`      | string  | ⚠️   | 认证令牌（打车类接口必需）                                                   |

---

## ⚠️ 参数校验约束

1. **所有时间戳必须是毫秒级**（13位数字），不是秒级
2. **城市编码必须是6位数字字符串**，如 `440100`
3. **经纬度必须是有效范围**：纬度 -90~90，经度 -180~180
4. **产品类型 prodType**：1=实时订单，2=预约订单
5. **create_ride_order 必须先调用 estimate_price**，获取 estimateId 后再调用
6. **phone必须是11位中国大陆手机号**

---

### 1. estimate_price - 价格预估

**必需参数（缺少任一将返回400错误）：**

| 参数名            | 类型    | 说明                   | 示例值                    |
| ----------------- | ------- | ---------------------- | ------------------------- |
| `platform`        | string  | 平台类型               | `Android`、`iOS`          |
| `deviceId`        | string  | 设备唯一标识           | `8ca4aa2dfa435aad`        |
| `deviceType`      | string  | 设备型号               | `华为荣耀9`               |
| `timestamp`       | integer | 毫秒级时间戳           | `1552451918000`           |
| `startLat`        | number  | 起点纬度               | `23.118531`               |
| `startLng`        | number  | 起点经度               | `113.332164`              |
| `endLat`          | number  | 终点纬度               | `23.128531`               |
| `endLng`          | number  | 终点经度               | `113.342164`              |
| `startAddress`    | string  | 起点地址               | `广州市天河区天河路385号` |
| `endAddress`      | string  | 终点地址               | `广州市天河区珠江新城`    |
| `fromCityCode`    | string  | 出发城市编码           | `440100`                  |
| `toCityCode`      | string  | 目的城市编码           | `440100`                  |
| `prodType`        | integer | 产品类型               | `1`(实时)、`2`(预约)      |
| `expectStartTime` | integer | 用车时间（秒级时间戳） | `1710000000`              |
| `passengerPhone`  | string  | 乘车人联系电话         | `13800138000`             |
| `scene`           | integer | 场景值                 | `1`                       |
| `sessionId`       | string  | BI跟踪会话ID           | `session-123456`          |
| `areaCode`        | string  | 市下一级行政编码       | `440106`                  |
| `channelDetailId` | string  | 营销渠道号             | `channel-123`             |
| `discountCode`    | string  | 折扣码                 | `DISCOUNT123`             |
| `multiRoute`      | boolean | 是否多路线             | `true`                    |

**可选参数：**

- `cityCode` - 城市编码（兼容旧参数名）
- `fromPoiId` - 出发地POI ID
- `toPoiId` - 目的地POI ID

---

### 2. create_ride_order - 创建打车订单

**⚠️ 前置条件：必须先调用 estimate_price 获取 estimateId**

**必需参数（缺少任一将返回400错误）：**

| 参数名                      | 类型    | 说明                                       | 示例值                           |
| --------------------------- | ------- | ------------------------------------------ | -------------------------------- |
| `platform`                  | string  | 平台类型                                   | `Android`、`iOS`                 |
| `deviceId`                  | string  | 设备唯一标识                               | `1`                              |
| `deviceType`                | string  | 设备型号                                   | `OPPO-PDNM00`                    |
| `timestamp`                 | integer | 毫秒级时间戳                               | `1773372870329`                  |
| `tdBlackBox`                | string  | 同盾指纹                                   | `1`                              |
| `token`                     | string  | 认证令牌                                   | `ruqimcp15577506988,15989070230` |
| `mobile`                    | string  | 乘客手机号码                               | `18826139823`                    |
| `priorityContact`           | integer | 优先联系人                                 | `1`(乘客)、`2`(乘车人)           |
| `expectStartTime`           | integer | 用车时间（秒级时间戳）                     | `1773372869`                     |
| `dispatchDuration`          | boolean | 是否返回派单时长                           | `false`                          |
| `submitLat`                 | number  | 提交位置纬度                               | `23.161564`                      |
| `submitLng`                 | number  | 提交位置经度                               | `113.473328`                     |
| `submitAddress`             | string  | 提交位置地址                               | `黄埔区PCI未来社区`              |
| `submitAddDtl`              | string  | 提交位置详细地址                           | `广东省广州市黄埔区新瑞路`       |
| `fromLat`                   | number  | 出发地纬度                                 | `23.0957223`                     |
| `fromLng`                   | number  | 出发地经度                                 | `113.3341985`                    |
| `fromAddress`               | string  | 出发地地址                                 | `赤岗[地铁站]C1口`               |
| `fromAddDtl`                | string  | 出发地详细地址                             | `赤岗[地铁站]C1口`               |
| `fromCityCode`              | string  | 出发城市编码                               | `440100`                         |
| `fromAdCode`                | string  | 出发地区域编码                             | `440105`                         |
| `fromCityName`              | string  | 出发城市名称                               | `广州市`                         |
| `toLat`                     | number  | 目的地纬度                                 | `23.098126`                      |
| `toLng`                     | number  | 目的地经度                                 | `113.366218`                     |
| `toAddress`                 | string  | 目的地地址                                 | `琶洲[地铁站]C口`                |
| `toAddDtl`                  | string  | 目的地详细地址                             | `琶洲[地铁站]C口`                |
| `toCityCode`                | string  | 目的城市编码                               | `440100`                         |
| `toAdCode`                  | string  | 目的地区域编码                             | `440105`                         |
| `toCityName`                | string  | 目的城市名称                               | `广州市`                         |
| `toPoiId`                   | string  | 目的地POI ID                               | `2199035519762`                  |
| `prodType`                  | string  | 产品类型                                   | `1`(实时)、`2`(预约)             |
| `routeId`                   | string  | 路线ID                                     | `5406931567564976608`            |
| `multiRoute`                | boolean | 是否多路线                                 | `true`                           |
| `orderSource`               | integer | 订单来源                                   | `0`                              |
| `type`                      | integer | 订单类型                                   | `0`                              |
| `estimateId`                | string  | 预估ID（**必须使用estimate_price返回的**） | `7616578458997722382`            |
| `sessionId`                 | string  | 会话ID                                     | `1773371746004`                  |
| `transportCarList`          | array   | 已勾选多运力列表                           | 见下方示例                       |
| `uncheckedTransportCarList` | array   | 未勾选运力列表                             | 见下方示例                       |
| `orderPattern`              | integer | 订单模式                                   | `1`                              |
| `checkOrderTimeCloseTo`     | boolean | 是否校验订单时间接近                       | `true`                           |

**transportCarList 格式示例：**

```json
[
  { "transportChannel": 1, "supplierId": 100, "carModelId": 1 },
  { "transportChannel": 1, "supplierId": 110, "carModelId": 1 }
]
```

---

### 3. query_ride_order - 查询打车订单

**必需参数：**

| 参数名       | 类型    | 说明         |
| ------------ | ------- | ------------ |
| `platform`   | string  | 平台类型     |
| `deviceId`   | string  | 设备唯一标识 |
| `deviceType` | string  | 设备型号     |
| `timestamp`  | integer | 毫秒级时间戳 |
| `token`      | string  | 认证令牌     |
| `orderId`    | string  | 订单ID       |

**订单状态处理：**

当接口返回 `orderState = 18`（待支付状态）时，必须向用户展示以下提示：

> 司机已到达目的地，当前订单已结束，麻烦到如祺出行APP支付这笔订单。欢迎下次再次乘车，谢谢！

---

### 4. query_order_list - 查询订单列表

**必需参数：**

| 参数名       | 类型    | 说明                                                                      |
| ------------ | ------- | ------------------------------------------------------------------------- |
| `platform`   | string  | 平台类型                                                                  |
| `deviceId`   | string  | 设备唯一标识                                                              |
| `deviceType` | string  | 设备型号                                                                  |
| `timestamp`  | integer | 毫秒级时间戳                                                              |
| `token`      | string  | 认证令牌                                                                  |
| `pageIndex`  | integer | 页码，从1开始                                                             |
| `pageSize`   | integer | 每页数量                                                                  |
| `type`       | string  | 查询类型：`1`(全部)、`2`(待支付)、`3`(待评价)、`4`(未完成)、`5`(发票列表) |

---

### 5. cancel_order - 取消订单

**必需参数：**

| 参数名       | 类型    | 说明         |
| ------------ | ------- | ------------ |
| `platform`   | string  | 平台类型     |
| `deviceId`   | string  | 设备唯一标识 |
| `deviceType` | string  | 设备型号     |
| `timestamp`  | integer | 毫秒级时间戳 |
| `token`      | string  | 认证令牌     |
| `orderId`    | string  | 订单ID       |

---

### 6. get_driver_location - 获取司机位置

**必需参数：**

| 参数名       | 类型    | 说明         |
| ------------ | ------- | ------------ |
| `platform`   | string  | 平台类型     |
| `deviceId`   | string  | 设备唯一标识 |
| `deviceType` | string  | 设备型号     |
| `timestamp`  | integer | 毫秒级时间戳 |
| `token`      | string  | 认证令牌     |
| `orderId`    | integer | 订单ID       |

---

### 7. reverse_geocode - 逆地理编码

**必需参数：**

| 参数名       | 类型    | 说明                                    |
| ------------ | ------- | --------------------------------------- |
| `platform`   | string  | 平台类型                                |
| `deviceId`   | string  | 设备唯一标识                            |
| `deviceType` | string  | 设备型号                                |
| `timestamp`  | integer | 毫秒级时间戳                            |
| `lat`        | number  | 纬度                                    |
| `lng`        | number  | 经度                                    |
| `getPoi`     | integer | 是否返回周边POI：`1`(返回)、`0`(不返回) |

---

### 8. driving_route_planning - 驾车路径规划

**必需参数：**

| 参数名             | 类型    | 说明                                                                                   |
| ------------------ | ------- | -------------------------------------------------------------------------------------- |
| `platform`         | string  | 平台类型                                                                               |
| `deviceId`         | string  | 设备唯一标识                                                                           |
| `deviceType`       | string  | 设备型号                                                                               |
| `timestamp`        | integer | 毫秒级时间戳                                                                           |
| `startLat`         | number  | 起点纬度                                                                               |
| `startLng`         | number  | 起点经度                                                                               |
| `endLat`           | number  | 终点纬度                                                                               |
| `endLng`           | number  | 终点经度                                                                               |
| `policy`           | integer | 策略：`1`(参考实时路况/时间最短)、`2`(网约车场景-接乘客)、`3`(网约车场景-送乘客)       |
| `preferencePolicy` | integer | 单项偏好：`1`(参考实时路况)、`2`(少收费)、`3`(不走高速)、`4`(使用地点出入口作为目的地) |

---

### 9. text_search - 文本搜索

**必需参数：**

| 参数名       | 类型    | 说明         |
| ------------ | ------- | ------------ |
| `platform`   | string  | 平台类型     |
| `deviceId`   | string  | 设备唯一标识 |
| `deviceType` | string  | 设备型号     |
| `timestamp`  | integer | 毫秒级时间戳 |
| `keyword`    | string  | 搜索关键词   |
| `region`     | string  | 搜索区域     |
| `cityCode`   | string  | 城市编码     |

**可选参数：**

- `latitude` - 纬度
- `longitude` - 经度

---

### 10. nearby_search - 周边检索

**必需参数：**

| 参数名       | 类型    | 说明           |
| ------------ | ------- | -------------- |
| `platform`   | string  | 平台类型       |
| `deviceId`   | string  | 设备唯一标识   |
| `deviceType` | string  | 设备型号       |
| `timestamp`  | integer | 毫秒级时间戳   |
| `latitude`   | number  | 纬度           |
| `longitude`  | number  | 经度           |
| `radius`     | integer | 搜索半径（米） |

---

### 11. get_recommended_boarding_point - 获取推荐上车点

**必需参数：**

| 参数名       | 类型    | 说明         |
| ------------ | ------- | ------------ |
| `platform`   | string  | 平台类型     |
| `deviceId`   | string  | 设备唯一标识 |
| `deviceType` | string  | 设备型号     |
| `timestamp`  | integer | 毫秒级时间戳 |
| `lat`        | number  | 纬度         |
| `lng`        | number  | 经度         |

---

## 错误诊断

| 错误           | 原因                               | 解决方法         |
| -------------- | ---------------------------------- | ---------------- |
| 400 错误       | RUQI_CLIENT_MCP_TOKEN 未配置或无效 | 配置环境变量     |
| 400 错误       | 参数格式不对                       | 检查参数格式     |
| "缺少必填参数" | 参数类型错误                       | 检查参数是否完整 |
