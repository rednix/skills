import axios from "axios";
import { token, env, config } from "./config.js";

// ---------- 飞书消息发送模块 ----------
async function getFeishuToken() {
  const url =
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal";
  const response = await axios.post(url, {
    app_id: config.feishu.appId,
    app_secret: config.feishu.appSecret,
  });
  return response.data.tenant_access_token;
}

/**
 * 发送飞书文本消息给指定用户
 * @param {string} openId 接收者的 open_id
 * @param {string} text 消息内容
 */
export async function sendFeishuMessage(openId, text) {
  try {
    const token = await getFeishuToken();
    const url =
      "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id";
    await axios.post(
      url,
      {
        receive_id: openId,
        msg_type: "text",
        content: JSON.stringify({ text }),
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );
    console.log(`✅ 飞书消息已发送至 ${openId}`);
  } catch (err) {
    console.error("❌ 飞书消息发送失败:", err.response?.data || err.message);
    throw err;
  }
}

// ---------- MCP 工具调用核心 ----------
/**
 * 通用 MCP 工具调用函数
 * @param {string} toolName 工具名
 * @param {object} args 参数
 * @returns {Promise<any>} 返回 MCP 响应的 result 部分，或 textContent（如果存在）
 */
const callMcpTool = async (toolName, args) => {
  try {
    const baseUrl = config.baseUrl[env];
    const baseParams = {
      platform: "Android",
      deviceId: "8ca4aa2dfa435aad",
      deviceType: "华为荣耀9",
      timestamp: Date.now(),
      tdBlackBox: "1234567890",
    };

    const requestBody = {
      jsonrpc: "2.0",
      id: Math.random().toString(36).substr(2, 9),
      method: "tools/call",
      params: {
        name: toolName,
        arguments: {
          ...baseParams,
          ...args,
          token, // 添加认证令牌
        },
      },
    };

    console.error("请求URL:", baseUrl);
    console.error("请求体:", JSON.stringify(requestBody, null, 2));

    const response = await axios.post(baseUrl, requestBody, {
      headers: { "Content-Type": "application/json" },
    });

    console.error("响应状态:", response.status);
    console.error("响应数据:", JSON.stringify(response.data, null, 2));

    if (response.data.error) {
      throw new Error(`MCP 调用错误: ${response.data.error.message}`);
    }

    const result = response.data.result;
    const textContent = result?.content?.[0]?.text;
    return textContent || result; // 返回文本或原始 result
  } catch (error) {
    console.error("MCP 调用失败:", error.message);
    if (error.response) {
      console.error("错误响应:", JSON.stringify(error.response.data, null, 2));
    }
    throw error;
  }
};

// ---------- 各个工具导出函数 ----------
export const estimatePrice = async (args) =>
  callMcpTool("estimate_price", args);
export const createRideOrder = async (args) =>
  callMcpTool("create_ride_order", args);
export const queryRideOrder = async (args) =>
  callMcpTool("query_ride_order", args);
export const queryOrderList = async (args) =>
  callMcpTool("query_order_list", args);
export const cancelOrder = async (args) => callMcpTool("cancel_order", args);
export const getDriverLocation = async (args) =>
  callMcpTool("get_driver_location", args);
export const reverseGeocode = async (args) =>
  callMcpTool("reverse_geocode", args);
export const drivingRoutePlanning = async (args) =>
  callMcpTool("driving_route_planning", args);
export const textSearch = async (args) => callMcpTool("text_search", args);
export const nearbySearch = async (args) => callMcpTool("nearby_search", args);
export const getRecommendedBoardingPoint = async (args) =>
  callMcpTool("get_recommended_boarding_point", args);

// 专门用于发送纯文本的工具（例如下单成功确认）
export const sendText = async (args) => {
  return args.text; // 直接返回文本，供命令行发送
};

// ---------- 命令行调用（工具名, open_id, 参数JSON）----------
// 用法：node mcp_client.js <toolName> [open_id] [argsJSON]
// 如果提供 open_id，则将结果通过飞书发送给该用户；否则打印结果到控制台
if (process.argv[2]) {
  const toolName = process.argv[2];
  const openId = process.argv[3] === "undefined" ? undefined : process.argv[3]; // 防止字符串 "undefined"
  const args = process.argv[4] ? JSON.parse(process.argv[4]) : {};

  const toolMap = {
    estimate_price: estimatePrice,
    create_ride_order: createRideOrder,
    query_ride_order: queryRideOrder,
    query_order_list: queryOrderList,
    cancel_order: cancelOrder,
    get_driver_location: getDriverLocation,
    reverse_geocode: reverseGeocode,
    driving_route_planning: drivingRoutePlanning,
    text_search: textSearch,
    nearby_search: nearbySearch,
    get_recommended_boarding_point: getRecommendedBoardingPoint,
    send_text: sendText,
  };

  if (toolMap[toolName]) {
    toolMap[toolName](args)
      .then(async (result) => {
        if (openId) {
          // 将结果格式化为可读文本
          let message = "";
          if (typeof result === "string") {
            message = result;
          } else {
            message = JSON.stringify(result, null, 2);
          }
          await sendFeishuMessage(openId, message);
          console.log(`✅ 结果已通过飞书发送给 ${openId}`);
        } else {
          // 没有 open_id，打印到控制台（供轮询脚本内部调用时使用）
          console.log(JSON.stringify(result, null, 2));
        }
      })
      .catch((error) => {
        console.error("执行失败:", error.message);
        process.exit(1);
      });
  } else {
    console.error(`未知工具: ${toolName}`);
    process.exit(1);
  }
}
