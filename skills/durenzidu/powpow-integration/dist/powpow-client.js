"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.PowpowAPIError = exports.PowpowClient = void 0;
const constants_1 = require("./utils/constants");
// 默认日志实现（如果未提供）
class DefaultLogger {
    debug(message, meta) {
        console.debug(`[DEBUG] ${message}`, meta || '');
    }
    info(message, meta) {
        console.info(`[INFO] ${message}`, meta || '');
    }
    warn(message, meta) {
        console.warn(`[WARN] ${message}`, meta || '');
    }
    error(message, error, meta) {
        console.error(`[ERROR] ${message}`, error?.message || '', meta || '');
    }
}
class PowpowClient {
    baseUrl;
    apiKey;
    authToken;
    eventSource;
    logger;
    // 重连状态
    reconnectAttempts = 0;
    reconnectTimeout;
    constructor(config) {
        this.baseUrl = config.baseUrl.replace(/\/$/, '');
        this.apiKey = config.apiKey;
        this.logger = config.logger || new DefaultLogger();
    }
    /**
     * 设置认证令牌
     */
    setAuthToken(token) {
        this.authToken = token;
        this.logger.debug('Auth token set', { tokenPrefix: token.substring(0, 10) + '...' });
    }
    /**
     * 获取请求头
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
        };
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        return headers;
    }
    /**
     * 带超时的fetch请求
     */
    async fetchWithTimeout(url, options, timeoutMs = constants_1.TIMEOUT_CONFIG.DEFAULT) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
            this.logger.warn(`Request timeout after ${timeoutMs}ms`, { url });
        }, timeoutMs);
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
            });
            clearTimeout(timeoutId);
            return response;
        }
        catch (error) {
            clearTimeout(timeoutId);
            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new PowpowAPIError('Request timeout', 408);
                }
            }
            throw error;
        }
    }
    /**
     * 注册用户
     * OpenClaw用户无账号时，引导注册POWPOW账号
     */
    async registerUser(params) {
        this.logger.info('Registering user', { username: params.username, email: params.email });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/openclaw/register`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(params),
        }, constants_1.TIMEOUT_CONFIG.REGISTRATION);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            this.logger.error('Registration failed', new Error(error.message), { status: response.status });
            throw new PowpowAPIError(`Registration failed: ${error.message || response.statusText}`, response.status);
        }
        const data = await response.json();
        this.setAuthToken(data.token);
        this.logger.info('User registered successfully', { userId: data.userId });
        return data;
    }
    /**
     * 用户登录
     * OpenClaw用户已有账号时，通过登录获取token
     */
    async loginUser(params) {
        this.logger.info('Logging in user', { username: params.username });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/openclaw/login`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(params),
        }, constants_1.TIMEOUT_CONFIG.LOGIN);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            this.logger.error('Login failed', new Error(error.message), { status: response.status });
            throw new PowpowAPIError(`Login failed: ${error.message || response.statusText}`, response.status);
        }
        const data = await response.json();
        this.setAuthToken(data.token);
        this.logger.info('User logged in successfully', { userId: data.userId });
        return data;
    }
    /**
     * 检查用户徽章余额
     */
    async checkBadges(userId) {
        this.logger.debug('Checking badges', { userId });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/openclaw/users/${userId}/badges`, {
            method: 'GET',
            headers: this.getHeaders(),
        }, constants_1.TIMEOUT_CONFIG.BADGE_CHECK);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            throw new PowpowAPIError(`Failed to check badges: ${error.message || response.statusText}`, response.status);
        }
        const data = await response.json();
        this.logger.debug('Badges retrieved', { userId, count: data.count });
        return data;
    }
    /**
     * 创建数字人
     * 需要2个徽章
     */
    async createDigitalHuman(params) {
        this.logger.info('Creating digital human', { name: params.name, userId: params.userId });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/openclaw/digital-humans`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
                ...params,
                source: 'openclaw',
            }),
        }, constants_1.TIMEOUT_CONFIG.DEFAULT);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            if (response.status === 402) {
                throw new PowpowAPIError('Insufficient badges. You need 2 badges to create a digital human.', 402);
            }
            this.logger.error('Failed to create digital human', new Error(error.message), { status: response.status });
            throw new PowpowAPIError(`Failed to create digital human: ${error.message || response.statusText}`, response.status);
        }
        const data = await response.json();
        this.logger.info('Digital human created', { dhId: data.id, name: data.name });
        return data;
    }
    /**
     * 获取用户的数字人列表
     */
    async getUserDigitalHumans(userId) {
        this.logger.debug('Getting digital humans', { userId });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/openclaw/users/${userId}/digital-humans`, {
            method: 'GET',
            headers: this.getHeaders(),
        }, constants_1.TIMEOUT_CONFIG.DEFAULT);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            throw new PowpowAPIError(`Failed to get digital humans: ${error.message || response.statusText}`, response.status);
        }
        const data = await response.json();
        this.logger.debug('Digital humans retrieved', { userId, count: data.length });
        return data;
    }
    /**
     * 续期数字人
     * 需要1个徽章，延长30天
     */
    async renewDigitalHuman(dhId) {
        this.logger.info('Renewing digital human', { dhId });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/openclaw/digital-humans/${dhId}/renew`, {
            method: 'POST',
            headers: this.getHeaders(),
        }, constants_1.TIMEOUT_CONFIG.DEFAULT);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            if (response.status === 402) {
                throw new PowpowAPIError('Insufficient badges. You need 1 badge to renew a digital human.', 402);
            }
            this.logger.error('Failed to renew digital human', new Error(error.message), { status: response.status });
            throw new PowpowAPIError(`Failed to renew digital human: ${error.message || response.statusText}`, response.status);
        }
        const data = await response.json();
        this.logger.info('Digital human renewed', { dhId, newExpiry: data.expiresAt });
        return data;
    }
    /**
     * 建立SSE连接，监听数字人回复
     * 修复：添加重连限制和指数退避
     */
    connectToDigitalHuman(dhId, onMessage, onError) {
        // 关闭已有连接和重连定时器
        this.disconnect();
        // 重置重连计数
        this.reconnectAttempts = 0;
        const tryConnect = () => {
            this.logger.debug('Attempting SSE connection', {
                dhId,
                attempt: this.reconnectAttempts + 1,
                maxAttempts: constants_1.RECONNECT_CONFIG.MAX_ATTEMPTS
            });
            // 使用Cookie传递认证信息，而不是URL参数
            const url = `${this.baseUrl}/api/digital-humans/${dhId}/chat`;
            this.eventSource = new EventSource(url, {
                withCredentials: true, // 发送Cookie
            });
            this.eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onMessage(data);
                    // 成功接收消息后重置重连计数
                    this.reconnectAttempts = 0;
                }
                catch (error) {
                    this.logger.error('Failed to parse SSE message', error);
                }
            };
            this.eventSource.onerror = (error) => {
                this.logger.warn('SSE connection error', {
                    dhId,
                    attempt: this.reconnectAttempts + 1,
                    error: error
                });
                // 检查是否超过最大重连次数
                if (this.reconnectAttempts >= constants_1.RECONNECT_CONFIG.MAX_ATTEMPTS) {
                    const finalError = new Error(`Failed to connect after ${constants_1.RECONNECT_CONFIG.MAX_ATTEMPTS} attempts`);
                    this.logger.error('Max reconnection attempts reached', finalError, { dhId });
                    if (onError)
                        onError(finalError);
                    this.disconnect();
                    return;
                }
                this.reconnectAttempts++;
                // 指数退避：延迟时间随重连次数增加
                const delay = Math.min(constants_1.RECONNECT_CONFIG.BASE_DELAY * Math.pow(2, this.reconnectAttempts - 1), constants_1.RECONNECT_CONFIG.MAX_DELAY);
                this.logger.info(`Reconnecting in ${delay}ms`, {
                    attempt: this.reconnectAttempts,
                    maxAttempts: constants_1.RECONNECT_CONFIG.MAX_ATTEMPTS
                });
                // 关闭当前连接
                if (this.eventSource) {
                    this.eventSource.close();
                    this.eventSource = undefined;
                }
                // 延迟重连
                this.reconnectTimeout = setTimeout(() => {
                    tryConnect();
                }, delay);
            };
            this.eventSource.onopen = () => {
                this.logger.info('SSE connection established', { dhId });
                // 连接成功后重置重连计数
                this.reconnectAttempts = 0;
            };
        };
        tryConnect();
    }
    /**
     * 发送消息给数字人
     */
    async sendMessage(dhId, message) {
        this.logger.debug('Sending message', { dhId, messageLength: message.length });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/digital-humans/${dhId}/chat`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ message }),
        }, constants_1.TIMEOUT_CONFIG.CHAT);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            throw new PowpowAPIError(`Failed to send message: ${error.message || response.statusText}`, response.status);
        }
        this.logger.debug('Message sent successfully', { dhId });
    }
    /**
     * 断开SSE连接
     */
    disconnect() {
        // 清除重连定时器
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = undefined;
        }
        // 关闭EventSource
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = undefined;
            this.logger.debug('SSE connection closed');
        }
        // 重置重连计数
        this.reconnectAttempts = 0;
    }
    /**
     * 获取数字人详情
     */
    async getDigitalHuman(dhId) {
        this.logger.debug('Getting digital human details', { dhId });
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/digital-humans/${dhId}`, {
            method: 'GET',
            headers: this.getHeaders(),
        }, constants_1.TIMEOUT_CONFIG.DEFAULT);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            throw new PowpowAPIError(`Failed to get digital human: ${error.message || response.statusText}`, response.status);
        }
        return response.json();
    }
}
exports.PowpowClient = PowpowClient;
/**
 * POWPOW API错误类
 */
class PowpowAPIError extends Error {
    statusCode;
    constructor(message, statusCode) {
        super(message);
        this.name = 'PowpowAPIError';
        this.statusCode = statusCode;
    }
}
exports.PowpowAPIError = PowpowAPIError;
//# sourceMappingURL=powpow-client.js.map