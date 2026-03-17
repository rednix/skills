/**
 * OpenClaw POWPOW Integration Skill
 *
 * 功能：
 * 1. POWPOW用户注册/登录
 * 2. 数字人创建与管理
 * 3. 与数字人实时通信
 *
 * 修复内容：
 * 1. 添加输入验证和XSS防护
 * 2. 添加速率限制
 * 3. 添加会话过期清理
 * 4. 优化错误处理
 * 5. 添加结构化日志
 *
 * @author OpenClaw Team
 * @version 1.1.0
 */
export interface PowpowSkillConfig {
    powpowBaseUrl: string;
    powpowApiKey?: string;
    defaultLocation?: {
        lat: number;
        lng: number;
        name: string;
    };
}
export declare class PowpowSkill implements Skill {
    name: string;
    description: string;
    version: string;
    private client;
    private config;
    private userSessions;
    private rateLimiter;
    private cleanupInterval?;
    private logger;
    capabilities: ({
        name: string;
        description: string;
        parameters: {
            username: {
                type: string;
                required: boolean;
                description: string;
            };
            email: {
                type: string;
                required: boolean;
                description: string;
            };
            password: {
                type: string;
                required: boolean;
                description: string;
            };
            name?: undefined;
            description?: undefined;
            lat?: undefined;
            lng?: undefined;
            locationName?: undefined;
            dhId?: undefined;
            message?: undefined;
        };
        handler: (params: {
            username: string;
            email: string;
            password: string;
        }, context: SkillContext) => Promise<string>;
    } | {
        name: string;
        description: string;
        parameters: {
            username: {
                type: string;
                required: boolean;
                description?: undefined;
            };
            password: {
                type: string;
                required: boolean;
                description?: undefined;
            };
            email?: undefined;
            name?: undefined;
            description?: undefined;
            lat?: undefined;
            lng?: undefined;
            locationName?: undefined;
            dhId?: undefined;
            message?: undefined;
        };
        handler: (params: {
            username: string;
            password: string;
        }, context: SkillContext) => Promise<string>;
    } | {
        name: string;
        description: string;
        parameters: {
            name: {
                type: string;
                required: boolean;
                description: string;
            };
            description: {
                type: string;
                required: boolean;
                description: string;
            };
            lat: {
                type: string;
                required: boolean;
                description: string;
            };
            lng: {
                type: string;
                required: boolean;
                description: string;
            };
            locationName: {
                type: string;
                required: boolean;
                description: string;
            };
            username?: undefined;
            email?: undefined;
            password?: undefined;
            dhId?: undefined;
            message?: undefined;
        };
        handler: (params: {
            name: string;
            description: string;
            lat?: number;
            lng?: number;
            locationName?: string;
        }, context: SkillContext) => Promise<string>;
    } | {
        name: string;
        description: string;
        parameters: {
            username?: undefined;
            email?: undefined;
            password?: undefined;
            name?: undefined;
            description?: undefined;
            lat?: undefined;
            lng?: undefined;
            locationName?: undefined;
            dhId?: undefined;
            message?: undefined;
        };
        handler: (params: {}, context: SkillContext) => Promise<string>;
    } | {
        name: string;
        description: string;
        parameters: {
            dhId: {
                type: string;
                required: boolean;
                description: string;
            };
            message: {
                type: string;
                required: boolean;
                description: string;
            };
            username?: undefined;
            email?: undefined;
            password?: undefined;
            name?: undefined;
            description?: undefined;
            lat?: undefined;
            lng?: undefined;
            locationName?: undefined;
        };
        handler: (params: {
            dhId: string;
            message: string;
        }, context: SkillContext) => Promise<string>;
    } | {
        name: string;
        description: string;
        parameters: {
            dhId: {
                type: string;
                required: boolean;
                description: string;
            };
            username?: undefined;
            email?: undefined;
            password?: undefined;
            name?: undefined;
            description?: undefined;
            lat?: undefined;
            lng?: undefined;
            locationName?: undefined;
            message?: undefined;
        };
        handler: (params: {
            dhId: string;
        }, context: SkillContext) => Promise<string>;
    })[];
    /**
     * Skill初始化
     */
    initialize(context: SkillContext): Promise<void>;
    /**
     * 获取或创建用户会话
     */
    private getSession;
    /**
     * 清理过期会话
     */
    private cleanupExpiredSessions;
    /**
     * 检查速率限制
     */
    private checkRateLimit;
    /**
     * 处理用户注册
     */
    private handleRegister;
    /**
     * 处理用户登录
     */
    private handleLogin;
    /**
     * 处理创建数字人
     */
    private handleCreateDigitalHuman;
    /**
     * 处理列出数字人
     */
    private handleListDigitalHumans;
    /**
     * 处理聊天
     */
    private handleChat;
    /**
     * 处理续期
     */
    private handleRenew;
    /**
     * 处理检查徽章
     */
    private handleCheckBadges;
    /**
     * 处理帮助
     */
    private handleHelp;
    /**
     * Skill清理
     */
    destroy(): Promise<void>;
}
export default PowpowSkill;
//# sourceMappingURL=index.d.ts.map