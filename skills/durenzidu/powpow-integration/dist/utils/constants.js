"use strict";
/**
 * 常量定义
 * 集中管理所有魔法数字和配置
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RATE_LIMIT_CONFIG = exports.VALIDATION_CONFIG = exports.TIMEOUT_CONFIG = exports.SESSION_CONFIG = exports.RECONNECT_CONFIG = void 0;
// 重连配置
exports.RECONNECT_CONFIG = {
    MAX_ATTEMPTS: 5,
    BASE_DELAY: 5000, // 5秒
    MAX_DELAY: 60000, // 60秒
};
// 会话配置
exports.SESSION_CONFIG = {
    TIMEOUT: 24 * 60 * 60 * 1000, // 24小时
    CLEANUP_INTERVAL: 60 * 60 * 1000, // 1小时清理一次
};
// 请求超时配置
exports.TIMEOUT_CONFIG = {
    DEFAULT: 30000, // 30秒
    REGISTRATION: 10000, // 10秒
    LOGIN: 10000, // 10秒
    CHAT: 60000, // 60秒（AI响应较慢）
    BADGE_CHECK: 5000, // 5秒
};
// 验证配置
exports.VALIDATION_CONFIG = {
    USERNAME_MIN: 3,
    USERNAME_MAX: 50,
    PASSWORD_MIN: 8,
    PASSWORD_MAX: 128,
    NAME_MIN: 1,
    NAME_MAX: 100,
    DESCRIPTION_MAX: 500,
};
// 速率限制配置
exports.RATE_LIMIT_CONFIG = {
    MAX_ATTEMPTS: 5,
    WINDOW_MS: 60000, // 1分钟
};
//# sourceMappingURL=constants.js.map