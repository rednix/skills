"use strict";
// @ts-nocheck
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.PowpowSkill = void 0;
const powpow_client_1 = require("./powpow-client");
const validator_1 = require("./utils/validator");
const rate_limiter_1 = require("./utils/rate-limiter");
const constants_1 = require("./utils/constants");
class PowpowSkill {
    name = 'powpow-integration';
    description = 'Integration with POWPOW platform for digital human management and communication';
    version = '1.1.0';
    client;
    config;
    userSessions = new Map();
    rateLimiter;
    cleanupInterval;
    logger;
    // 能力定义
    capabilities = [
        {
            name: 'register',
            description: 'Register a new POWPOW account',
            parameters: {
                username: { type: 'string', required: true, description: 'Username for POWPOW (3-50 chars, alphanumeric)' },
                email: { type: 'string', required: true, description: 'Valid email address' },
                password: { type: 'string', required: true, description: 'Password (min 8 chars, must include uppercase, lowercase, number)' },
            },
            handler: this.handleRegister.bind(this),
        },
        {
            name: 'login',
            description: 'Login to existing POWPOW account',
            parameters: {
                username: { type: 'string', required: true },
                password: { type: 'string', required: true },
            },
            handler: this.handleLogin.bind(this),
        },
        {
            name: 'createDigitalHuman',
            description: 'Create a digital human on POWPOW map (requires 2 badges)',
            parameters: {
                name: { type: 'string', required: true, description: 'Digital human name (1-100 chars)' },
                description: { type: 'string', required: true, description: 'Description/personality (max 500 chars)' },
                lat: { type: 'number', required: false, description: 'Latitude (-90 to 90)' },
                lng: { type: 'number', required: false, description: 'Longitude (-180 to 180)' },
                locationName: { type: 'string', required: false, description: 'Location name' },
            },
            handler: this.handleCreateDigitalHuman.bind(this),
        },
        {
            name: 'listDigitalHumans',
            description: 'List all your digital humans',
            parameters: {},
            handler: this.handleListDigitalHumans.bind(this),
        },
        {
            name: 'chat',
            description: 'Start chatting with a digital human',
            parameters: {
                dhId: { type: 'string', required: true, description: 'Digital human ID' },
                message: { type: 'string', required: true, description: 'Message to send (max 2000 chars)' },
            },
            handler: this.handleChat.bind(this),
        },
        {
            name: 'renew',
            description: 'Renew a digital human for 30 days (requires 1 badge)',
            parameters: {
                dhId: { type: 'string', required: true, description: 'Digital human ID to renew' },
            },
            handler: this.handleRenew.bind(this),
        },
        {
            name: 'checkBadges',
            description: 'Check your badge balance',
            parameters: {},
            handler: this.handleCheckBadges.bind(this),
        },
        {
            name: 'help',
            description: 'Show available commands',
            parameters: {},
            handler: this.handleHelp.bind(this),
        },
    ];
    /**
     * Skill初始化
     */
    async initialize(context) {
        this.config = context.getConfig('powpow');
        if (!this.config?.powpowBaseUrl) {
            throw new Error('POWPOW base URL is required in skill configuration');
        }
        // 初始化日志
        this.logger = {
            debug: (msg, meta) => context.logger.debug(`[POWPOW] ${msg}`, meta),
            info: (msg, meta) => context.logger.info(`[POWPOW] ${msg}`, meta),
            warn: (msg, meta) => context.logger.warn(`[POWPOW] ${msg}`, meta),
            error: (msg, err, meta) => context.logger.error(`[POWPOW] ${msg}`, err, meta),
        };
        // 初始化客户端
        this.client = new powpow_client_1.PowpowClient({
            baseUrl: this.config.powpowBaseUrl,
            apiKey: this.config.powpowApiKey,
            logger: this.logger,
        });
        // 初始化速率限制器
        this.rateLimiter = new rate_limiter_1.RateLimiter();
        // 启动会话清理定时器
        this.cleanupInterval = setInterval(() => {
            this.cleanupExpiredSessions();
        }, constants_1.SESSION_CONFIG.CLEANUP_INTERVAL);
        this.logger.info('POWPOW skill initialized', {
            baseUrl: this.config.powpowBaseUrl,
            hasApiKey: !!this.config.powpowApiKey,
        });
    }
    /**
     * 获取或创建用户会话
     */
    getSession(userId) {
        if (!this.userSessions.has(userId)) {
            this.userSessions.set(userId, {
                isChatting: false,
                lastActivity: Date.now()
            });
        }
        else {
            // 更新活动时间
            const session = this.userSessions.get(userId);
            session.lastActivity = Date.now();
        }
        return this.userSessions.get(userId);
    }
    /**
     * 清理过期会话
     */
    cleanupExpiredSessions() {
        const now = Date.now();
        let cleanedCount = 0;
        for (const [userId, session] of this.userSessions.entries()) {
            if (now - session.lastActivity > constants_1.SESSION_CONFIG.TIMEOUT) {
                // 如果正在聊天，先断开连接
                if (session.isChatting) {
                    this.client.disconnect();
                }
                this.userSessions.delete(userId);
                cleanedCount++;
            }
        }
        if (cleanedCount > 0) {
            this.logger.info(`Cleaned up ${cleanedCount} expired sessions`);
        }
    }
    /**
     * 检查速率限制
     */
    checkRateLimit(userId, action) {
        if (!this.rateLimiter.isAllowed(userId)) {
            const resetTime = this.rateLimiter.getResetTime(userId);
            const waitSeconds = resetTime ? Math.ceil((resetTime - Date.now()) / 1000) : 60;
            return `❌ Rate limit exceeded. Please try again in ${waitSeconds} seconds.`;
        }
        return null;
    }
    /**
     * 处理用户注册
     */
    async handleRegister(params, context) {
        // 速率限制检查
        const rateLimitError = this.checkRateLimit(context.userId, 'register');
        if (rateLimitError)
            return rateLimitError;
        // 验证用户名
        const usernameValidation = validator_1.Validator.validateUsername(params.username);
        if (!usernameValidation.valid) {
            return `❌ ${usernameValidation.error}`;
        }
        // 验证邮箱
        const emailValidation = validator_1.Validator.validateEmail(params.email);
        if (!emailValidation.valid) {
            return `❌ ${emailValidation.error}`;
        }
        // 验证密码
        const passwordValidation = validator_1.Validator.validatePassword(params.password);
        if (!passwordValidation.valid) {
            return `❌ ${passwordValidation.error}`;
        }
        this.logger.info('Processing registration', {
            username: params.username,
            email: params.email,
            openclawUserId: context.userId
        });
        try {
            const result = await this.client.registerUser({
                username: validator_1.Validator.sanitizeString(params.username),
                email: validator_1.Validator.sanitizeString(params.email),
                password: params.password, // 密码不清理，会被哈希
                source: 'openclaw',
                openclawUserId: context.userId,
            });
            // 保存会话
            const session = this.getSession(context.userId);
            session.powpowUserId = result.userId;
            session.powpowToken = result.token;
            this.client.setAuthToken(result.token);
            // 清除速率限制记录（注册成功）
            this.rateLimiter.clearForKey(context.userId);
            this.logger.info('Registration successful', {
                powpowUserId: result.userId,
                openclawUserId: context.userId
            });
            return `✅ Registration successful!\n` +
                `👤 User ID: ${result.userId}\n` +
                `🏅 Initial badges: ${result.badges.count}\n` +
                `\nYou can now create digital humans using the 'createDigitalHuman' command.`;
        }
        catch (error) {
            if (error instanceof powpow_client_1.PowpowAPIError) {
                this.logger.error('Registration failed', error, {
                    username: params.username,
                    status: error.statusCode
                });
                return `❌ Registration failed: ${error.message}`;
            }
            this.logger.error('Unexpected registration error', error);
            return '❌ An unexpected error occurred during registration.';
        }
    }
    /**
     * 处理用户登录
     */
    async handleLogin(params, context) {
        // 速率限制检查
        const rateLimitError = this.checkRateLimit(context.userId, 'login');
        if (rateLimitError)
            return rateLimitError;
        // 验证用户名
        const usernameValidation = validator_1.Validator.validateUsername(params.username);
        if (!usernameValidation.valid) {
            return `❌ ${usernameValidation.error}`;
        }
        // 验证密码存在
        if (!params.password || params.password.length < 1) {
            return '❌ Password is required';
        }
        this.logger.info('Processing login', {
            username: params.username,
            openclawUserId: context.userId
        });
        try {
            const result = await this.client.loginUser({
                username: validator_1.Validator.sanitizeString(params.username),
                password: params.password,
            });
            // 保存会话
            const session = this.getSession(context.userId);
            session.powpowUserId = result.userId;
            session.powpowToken = result.token;
            this.client.setAuthToken(result.token);
            // 清除速率限制记录（登录成功）
            this.rateLimiter.clearForKey(context.userId);
            this.logger.info('Login successful', {
                powpowUserId: result.userId,
                openclawUserId: context.userId
            });
            return `✅ Login successful!\n` +
                `👤 User ID: ${result.userId}\n` +
                `🏅 Available badges: ${result.badges.count}`;
        }
        catch (error) {
            if (error instanceof powpow_client_1.PowpowAPIError) {
                this.logger.warn('Login failed', {
                    username: params.username,
                    status: error.statusCode
                });
                return `❌ Login failed: ${error.message}`;
            }
            this.logger.error('Unexpected login error', error);
            return '❌ An unexpected error occurred during login.';
        }
    }
    /**
     * 处理创建数字人
     */
    async handleCreateDigitalHuman(params, context) {
        const session = this.getSession(context.userId);
        // 检查是否已登录
        if (!session.powpowUserId) {
            return '⚠️ Please login first using: login username=<your_username> password=<your_password>';
        }
        // 验证名称
        const nameValidation = validator_1.Validator.validateDigitalHumanName(params.name);
        if (!nameValidation.valid) {
            return `❌ ${nameValidation.error}`;
        }
        // 验证描述
        const descValidation = validator_1.Validator.validateDescription(params.description);
        if (!descValidation.valid) {
            return `❌ ${descValidation.error}`;
        }
        // 验证坐标
        const lat = params.lat ?? this.config.defaultLocation?.lat ?? 39.9042;
        const lng = params.lng ?? this.config.defaultLocation?.lng ?? 116.4074;
        const coordValidation = validator_1.Validator.validateCoordinates(lat, lng);
        if (!coordValidation.valid) {
            return `❌ ${coordValidation.error}`;
        }
        const locationName = params.locationName
            ? validator_1.Validator.sanitizeString(params.locationName)
            : this.config.defaultLocation?.name ?? 'Beijing';
        this.logger.info('Creating digital human', {
            name: params.name,
            userId: session.powpowUserId
        });
        try {
            const dh = await this.client.createDigitalHuman({
                name: validator_1.Validator.sanitizeString(params.name),
                description: validator_1.Validator.sanitizeString(params.description),
                lat,
                lng,
                locationName,
                userId: session.powpowUserId,
            });
            // 保存当前数字人
            session.currentDigitalHuman = dh;
            this.logger.info('Digital human created', {
                dhId: dh.id,
                name: dh.name
            });
            return `✅ Digital human created successfully!\n` +
                `🎭 Name: ${dh.name}\n` +
                `🆔 ID: ${dh.id}\n` +
                `📍 Location: ${dh.locationName} (${dh.lat}, ${dh.lng})\n` +
                `⏰ Expires at: ${new Date(dh.expiresAt).toLocaleString()}\n` +
                `\nYou can now chat with it using: chat dhId=${dh.id} message=<your_message>`;
        }
        catch (error) {
            if (error instanceof powpow_client_1.PowpowAPIError) {
                if (error.statusCode === 402) {
                    return `❌ ${error.message}\n\n` +
                        `You can check your badge balance using: checkBadges`;
                }
                this.logger.error('Failed to create digital human', error);
                return `❌ Failed to create digital human: ${error.message}`;
            }
            this.logger.error('Unexpected error creating digital human', error);
            return '❌ An unexpected error occurred.';
        }
    }
    /**
     * 处理列出数字人
     */
    async handleListDigitalHumans(params, context) {
        const session = this.getSession(context.userId);
        if (!session.powpowUserId) {
            return '⚠️ Please login first using: login username=<your_username> password=<your_password>';
        }
        try {
            const dhs = await this.client.getUserDigitalHumans(session.powpowUserId);
            if (dhs.length === 0) {
                return '📭 You have no digital humans yet.\n' +
                    'Create one using: createDigitalHuman name=<name> description=<description>';
            }
            let response = `🎭 You have ${dhs.length} digital human(s):\n\n`;
            dhs.forEach((dh, index) => {
                const daysLeft = Math.ceil((new Date(dh.expiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
                const status = dh.isActive ? '✅' : '❌';
                response += `${index + 1}. ${status} ${dh.name}\n` +
                    `   ID: ${dh.id}\n` +
                    `   📍 ${dh.locationName}\n` +
                    `   ⏰ ${daysLeft} days left\n` +
                    `   💬 Chat: chat dhId=${dh.id} message=hello\n\n`;
            });
            return response;
        }
        catch (error) {
            if (error instanceof powpow_client_1.PowpowAPIError) {
                this.logger.error('Failed to list digital humans', error);
                return `❌ Failed to list digital humans: ${error.message}`;
            }
            this.logger.error('Unexpected error listing digital humans', error);
            return '❌ An unexpected error occurred.';
        }
    }
    /**
     * 处理聊天
     */
    async handleChat(params, context) {
        const session = this.getSession(context.userId);
        if (!session.powpowUserId) {
            return '⚠️ Please login first';
        }
        // 验证数字人ID
        const dhIdValidation = validator_1.Validator.validateDigitalHumanId(params.dhId);
        if (!dhIdValidation.valid) {
            return `❌ ${dhIdValidation.error}`;
        }
        // 验证消息
        const messageValidation = validator_1.Validator.validateMessage(params.message);
        if (!messageValidation.valid) {
            return `❌ ${messageValidation.error}`;
        }
        // 如果已经在聊天中，先断开
        if (session.isChatting) {
            this.client.disconnect();
            session.isChatting = false;
        }
        this.logger.info('Starting chat', {
            dhId: params.dhId,
            userId: session.powpowUserId
        });
        try {
            // 建立SSE连接
            this.client.connectToDigitalHuman(params.dhId, (message) => {
                // 收到数字人回复，通过OpenClaw发送给用户
                context.sendMessage({
                    content: message.content,
                    metadata: {
                        sender: 'digital_human',
                        timestamp: message.timestamp,
                    },
                });
            }, (error) => {
                this.logger.error('Chat connection error', error, { dhId: params.dhId });
                context.sendMessage({
                    content: '⚠️ Connection lost. Please try again.',
                });
                session.isChatting = false;
            });
            session.isChatting = true;
            // 发送用户消息
            await this.client.sendMessage(params.dhId, params.message);
            return `💬 Message sent to digital human. Waiting for response...`;
        }
        catch (error) {
            session.isChatting = false;
            if (error instanceof powpow_client_1.PowpowAPIError) {
                this.logger.error('Chat failed', error, { dhId: params.dhId });
                return `❌ Chat failed: ${error.message}`;
            }
            this.logger.error('Unexpected chat error', error, { dhId: params.dhId });
            return '❌ An unexpected error occurred.';
        }
    }
    /**
     * 处理续期
     */
    async handleRenew(params, context) {
        const session = this.getSession(context.userId);
        if (!session.powpowUserId) {
            return '⚠️ Please login first';
        }
        // 验证数字人ID
        const dhIdValidation = validator_1.Validator.validateDigitalHumanId(params.dhId);
        if (!dhIdValidation.valid) {
            return `❌ ${dhIdValidation.error}`;
        }
        this.logger.info('Renewing digital human', {
            dhId: params.dhId,
            userId: session.powpowUserId
        });
        try {
            const dh = await this.client.renewDigitalHuman(params.dhId);
            this.logger.info('Digital human renewed', {
                dhId: params.dhId,
                newExpiry: dh.expiresAt
            });
            return `✅ Digital human renewed successfully!\n` +
                `🎭 Name: ${dh.name}\n` +
                `⏰ New expiration: ${new Date(dh.expiresAt).toLocaleString()}\n` +
                `📅 Extended by 30 days`;
        }
        catch (error) {
            if (error instanceof powpow_client_1.PowpowAPIError) {
                if (error.statusCode === 402) {
                    return `❌ ${error.message}`;
                }
                this.logger.error('Failed to renew digital human', error);
                return `❌ Failed to renew: ${error.message}`;
            }
            this.logger.error('Unexpected error renewing digital human', error);
            return '❌ An unexpected error occurred.';
        }
    }
    /**
     * 处理检查徽章
     */
    async handleCheckBadges(params, context) {
        const session = this.getSession(context.userId);
        if (!session.powpowUserId) {
            return '⚠️ Please login first';
        }
        try {
            const badges = await this.client.checkBadges(session.powpowUserId);
            return `🏅 Your badge balance:\n` +
                `   Count: ${badges.count}\n` +
                `   Type: ${badges.type}\n\n` +
                `💡 You need:\n` +
                `   • 2 badges to create a digital human\n` +
                `   • 1 badge to renew a digital human`;
        }
        catch (error) {
            if (error instanceof powpow_client_1.PowpowAPIError) {
                this.logger.error('Failed to check badges', error);
                return `❌ Failed to check badges: ${error.message}`;
            }
            this.logger.error('Unexpected error checking badges', error);
            return '❌ An unexpected error occurred.';
        }
    }
    /**
     * 处理帮助
     */
    async handleHelp(params, context) {
        return `🎭 POWPOW Digital Human Skill - Available Commands\n\n` +
            `Authentication:\n` +
            `  • register username=<name> email=<email> password=<pwd> - Create new account\n` +
            `  • login username=<name> password=<pwd> - Login to existing account\n\n` +
            `Digital Human Management:\n` +
            `  • createDigitalHuman name=<name> description=<desc> [lat=<lat> lng=<lng>] - Create (2 badges)\n` +
            `  • listDigitalHumans - List all your digital humans\n` +
            `  • renew dhId=<id> - Renew for 30 days (1 badge)\n\n` +
            `Communication:\n` +
            `  • chat dhId=<id> message=<text> - Chat with a digital human\n\n` +
            `Account:\n` +
            `  • checkBadges - Check your badge balance\n` +
            `  • help - Show this help message`;
    }
    /**
     * Skill清理
     */
    async destroy() {
        // 停止会话清理定时器
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
            this.cleanupInterval = undefined;
        }
        // 断开所有SSE连接
        this.client.disconnect();
        // 清理会话
        this.userSessions.clear();
        // 清理速率限制记录
        this.rateLimiter.clear();
        this.logger.info('POWPOW skill destroyed');
    }
}
exports.PowpowSkill = PowpowSkill;
// 导出Skill类
exports.default = PowpowSkill;
//# sourceMappingURL=index.js.map