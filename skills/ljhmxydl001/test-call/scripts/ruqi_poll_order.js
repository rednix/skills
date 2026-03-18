#!/usr/bin/env node
import { queryRideOrder, sendFeishuMessage } from "./mcp_client.js";

const POLL_INTERVAL = 5000; // 5秒

const STATE_MAP = {
  3: "指派中",
  4: "已接单",
  5: "已发车",
  6: "已到达",
  7: "服务中",
  8: "服务已结束",
  9: "已完成",
  10: "已取消",
  17: "免密待支付",
  18: "待支付",
};
const TERMINAL_STATES = [9, 10, 17, 18]; // 状态 >8

const orderId = process.argv[2];
const openId = process.argv[3];

if (!orderId || !openId) {
  console.error("用法: node polling.js <orderId> <openId>");
  process.exit(1);
}

console.log(`开始监控订单 ${orderId}，用户 ${openId}`);
let lastStatus = null;

async function checkStatus() {
  try {
    const args = {
      platform: "Android",
      deviceId: "8ca4aa2dfa435aad",
      deviceType: "华为荣耀9",
      timestamp: Date.now(),
      orderId,
    };
    const result = await queryRideOrder(args);
    let currentState = null;
    if (typeof result === "string") {
      try {
        const parsed = JSON.parse(result);
        currentState = parsed?.data?.orderState ?? parsed?.orderState;
      } catch {
        const match = result.match(/orderState[=:](\d+)/);
        if (match) currentState = parseInt(match[1], 10);
      }
    } else if (result && typeof result === "object") {
      currentState = result?.data?.orderState ?? result?.orderState;
    }

    if (currentState === null) {
      console.error(`订单 ${orderId} 无法解析状态，跳过本次轮询`);
      return;
    }

    if (lastStatus !== currentState) {
      console.log(`订单 ${orderId} 状态变化: ${lastStatus} -> ${currentState}`);
      const desc = STATE_MAP[currentState] || `未知状态(${currentState})`;
      const message = `订单 ${orderId} 状态更新：${desc}`;
      await sendFeishuMessage(openId, message);
      lastStatus = currentState;
    }

    if (TERMINAL_STATES.includes(currentState)) {
      console.log(`订单 ${orderId} 已进入终态，停止监控`);
      process.exit(0);
    }
  } catch (err) {
    console.error(`轮询订单 ${orderId} 出错:`, err.message);
  }
}

checkStatus();
setInterval(checkStatus, POLL_INTERVAL);
