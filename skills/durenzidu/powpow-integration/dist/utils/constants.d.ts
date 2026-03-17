/**
 * 常量定义
 * 集中管理所有魔法数字和配置
 */
export declare const RECONNECT_CONFIG: {
    readonly MAX_ATTEMPTS: 5;
    readonly BASE_DELAY: 5000;
    readonly MAX_DELAY: 60000;
};
export declare const SESSION_CONFIG: {
    readonly TIMEOUT: number;
    readonly CLEANUP_INTERVAL: number;
};
export declare const TIMEOUT_CONFIG: {
    readonly DEFAULT: 30000;
    readonly REGISTRATION: 10000;
    readonly LOGIN: 10000;
    readonly CHAT: 60000;
    readonly BADGE_CHECK: 5000;
};
export declare const VALIDATION_CONFIG: {
    readonly USERNAME_MIN: 3;
    readonly USERNAME_MAX: 50;
    readonly PASSWORD_MIN: 8;
    readonly PASSWORD_MAX: 128;
    readonly NAME_MIN: 1;
    readonly NAME_MAX: 100;
    readonly DESCRIPTION_MAX: 500;
};
export declare const RATE_LIMIT_CONFIG: {
    readonly MAX_ATTEMPTS: 5;
    readonly WINDOW_MS: 60000;
};
//# sourceMappingURL=constants.d.ts.map