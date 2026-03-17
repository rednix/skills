/**
 * POWPOW API Client
 * 用于OpenClaw与POWPOW平台的通信
 *
 * 修复内容：
 * 1. 添加SSE重连限制，防止无限重连
 * 2. 使用Cookie替代URL参数传递Token，提升安全性
 * 3. 添加请求超时机制
 * 4. 添加结构化日志
 * 5. 优化错误处理
 */
export interface Logger {
    debug(message: string, meta?: Record<string, unknown>): void;
    info(message: string, meta?: Record<string, unknown>): void;
    warn(message: string, meta?: Record<string, unknown>): void;
    error(message: string, error?: Error, meta?: Record<string, unknown>): void;
}
export interface PowpowConfig {
    baseUrl: string;
    apiKey?: string;
    logger?: Logger;
}
export interface UserRegistrationParams {
    username: string;
    email: string;
    password: string;
    source: 'openclaw';
    openclawUserId: string;
}
export interface UserLoginParams {
    username: string;
    password: string;
}
export interface CreateDigitalHumanParams {
    name: string;
    description: string;
    avatarUrl?: string;
    lat: number;
    lng: number;
    locationName?: string;
    userId: string;
}
export interface DigitalHuman {
    id: string;
    name: string;
    description: string;
    avatarUrl?: string;
    lat: number;
    lng: number;
    locationName?: string;
    expiresAt: string;
    createdAt: string;
    isActive: boolean;
}
export interface ChatMessage {
    id: string;
    content: string;
    sender: 'user' | 'digital_human';
    timestamp: string;
}
export type BadgeType = 'standard' | 'premium' | 'vip';
export interface BadgeInfo {
    count: number;
    type: BadgeType;
}
export declare class PowpowClient {
    private baseUrl;
    private apiKey?;
    private authToken?;
    private eventSource?;
    private logger;
    private reconnectAttempts;
    private reconnectTimeout?;
    constructor(config: PowpowConfig);
    /**
     * 设置认证令牌
     */
    setAuthToken(token: string): void;
    /**
     * 获取请求头
     */
    private getHeaders;
    /**
     * 带超时的fetch请求
     */
    private fetchWithTimeout;
    /**
     * 注册用户
     * OpenClaw用户无账号时，引导注册POWPOW账号
     */
    registerUser(params: UserRegistrationParams): Promise<{
        userId: string;
        token: string;
        badges: BadgeInfo;
    }>;
    /**
     * 用户登录
     * OpenClaw用户已有账号时，通过登录获取token
     */
    loginUser(params: UserLoginParams): Promise<{
        userId: string;
        token: string;
        badges: BadgeInfo;
    }>;
    /**
     * 检查用户徽章余额
     */
    checkBadges(userId: string): Promise<BadgeInfo>;
    /**
     * 创建数字人
     * 需要2个徽章
     */
    createDigitalHuman(params: CreateDigitalHumanParams): Promise<DigitalHuman>;
    /**
     * 获取用户的数字人列表
     */
    getUserDigitalHumans(userId: string): Promise<DigitalHuman[]>;
    /**
     * 续期数字人
     * 需要1个徽章，延长30天
     */
    renewDigitalHuman(dhId: string): Promise<DigitalHuman>;
    /**
     * 建立SSE连接，监听数字人回复
     * 修复：添加重连限制和指数退避
     */
    connectToDigitalHuman(dhId: string, onMessage: (message: ChatMessage) => void, onError?: (error: Error) => void): void;
    /**
     * 发送消息给数字人
     */
    sendMessage(dhId: string, message: string): Promise<void>;
    /**
     * 断开SSE连接
     */
    disconnect(): void;
    /**
     * 获取数字人详情
     */
    getDigitalHuman(dhId: string): Promise<DigitalHuman>;
}
/**
 * POWPOW API错误类
 */
export declare class PowpowAPIError extends Error {
    statusCode: number;
    constructor(message: string, statusCode: number);
}
//# sourceMappingURL=powpow-client.d.ts.map