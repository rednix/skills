/**
 * 速率限制器
 * 防止暴力破解和滥用
 */
export declare class RateLimiter {
    private attempts;
    /**
     * 检查是否允许请求
     * @param key 标识符（如用户ID或IP）
     * @returns 是否允许
     */
    isAllowed(key: string): boolean;
    /**
     * 获取剩余尝试次数
     */
    getRemainingAttempts(key: string): number;
    /**
     * 获取下次重置时间
     */
    getResetTime(key: string): number | null;
    /**
     * 清理所有记录
     */
    clear(): void;
    /**
     * 清理特定用户的记录
     */
    clearForKey(key: string): void;
}
//# sourceMappingURL=rate-limiter.d.ts.map