"use strict";
/**
 * 速率限制器
 * 防止暴力破解和滥用
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RateLimiter = void 0;
const constants_1 = require("./constants");
class RateLimiter {
    attempts = new Map();
    /**
     * 检查是否允许请求
     * @param key 标识符（如用户ID或IP）
     * @returns 是否允许
     */
    isAllowed(key) {
        const now = Date.now();
        const windowStart = now - constants_1.RATE_LIMIT_CONFIG.WINDOW_MS;
        // 获取或创建条目
        let entry = this.attempts.get(key);
        if (!entry) {
            entry = { attempts: [] };
            this.attempts.set(key, entry);
        }
        // 清理过期记录
        entry.attempts = entry.attempts.filter(time => time > windowStart);
        // 检查是否超过限制
        if (entry.attempts.length >= constants_1.RATE_LIMIT_CONFIG.MAX_ATTEMPTS) {
            return false;
        }
        // 记录本次尝试
        entry.attempts.push(now);
        return true;
    }
    /**
     * 获取剩余尝试次数
     */
    getRemainingAttempts(key) {
        const now = Date.now();
        const windowStart = now - constants_1.RATE_LIMIT_CONFIG.WINDOW_MS;
        const entry = this.attempts.get(key);
        if (!entry) {
            return constants_1.RATE_LIMIT_CONFIG.MAX_ATTEMPTS;
        }
        const recentAttempts = entry.attempts.filter(time => time > windowStart);
        return Math.max(0, constants_1.RATE_LIMIT_CONFIG.MAX_ATTEMPTS - recentAttempts.length);
    }
    /**
     * 获取下次重置时间
     */
    getResetTime(key) {
        const entry = this.attempts.get(key);
        if (!entry || entry.attempts.length === 0) {
            return null;
        }
        const oldestAttempt = Math.min(...entry.attempts);
        return oldestAttempt + constants_1.RATE_LIMIT_CONFIG.WINDOW_MS;
    }
    /**
     * 清理所有记录
     */
    clear() {
        this.attempts.clear();
    }
    /**
     * 清理特定用户的记录
     */
    clearForKey(key) {
        this.attempts.delete(key);
    }
}
exports.RateLimiter = RateLimiter;
//# sourceMappingURL=rate-limiter.js.map