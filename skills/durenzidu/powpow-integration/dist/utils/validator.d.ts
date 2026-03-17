/**
 * 输入验证工具类
 * 提供各种验证和清理功能
 */
export interface ValidationResult {
    valid: boolean;
    error?: string;
}
export declare class Validator {
    /**
     * 验证邮箱格式
     */
    static validateEmail(email: string): ValidationResult;
    /**
     * 验证用户名
     */
    static validateUsername(username: string): ValidationResult;
    /**
     * 验证密码
     */
    static validatePassword(password: string): ValidationResult;
    /**
     * 验证数字人名称
     */
    static validateDigitalHumanName(name: string): ValidationResult;
    /**
     * 验证数字人描述
     */
    static validateDescription(description: string): ValidationResult;
    /**
     * 验证坐标
     */
    static validateCoordinates(lat: number, lng: number): ValidationResult;
    /**
     * 验证数字人ID
     */
    static validateDigitalHumanId(dhId: string): ValidationResult;
    /**
     * 清理字符串（防止XSS）
     */
    static sanitizeString(input: string): string;
    /**
     * 清理对象中的所有字符串属性
     */
    static sanitizeObject<T extends Record<string, unknown>>(obj: T): T;
    /**
     * 验证消息内容
     */
    static validateMessage(message: string): ValidationResult;
}
//# sourceMappingURL=validator.d.ts.map