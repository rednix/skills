"""
安全白名单模块 - 增强版 v2.0
Security Allowlist Module - Enhanced v2.0

⚠️ 注意 / Note:
此模块定义推荐的命令白名单，作为安全最佳实践的文档。
This module defines a recommended command allowlist as documentation of security best practices.

实际的命令执行安全控制由 OpenClaw Gateway 运行时提供。
Actual command execution security is enforced by OpenClaw Gateway runtime.

v2.0 更新:
- ✅ 路径遍历防护
- ✅ 命令注入防护增强
- ✅ 输入验证
- ✅ 安全日志记录
- ✅ 敏感信息检测

用途 / Purpose:
1. 文档化安全边界 / Document security boundaries
2. 本地开发时的参考 / Reference for local development
3. 可选的安全增强 / Optional security enhancement

依赖 / Dependencies:
- 此模块是参考实现，不强制调用
- This module is a reference implementation, not mandatorily invoked
- 最终安全由 OpenClaw Gateway 控制
- Final security is controlled by OpenClaw Gateway
"""

import shlex
import re
import os
import logging
from typing import Tuple, List, Dict, Any, Optional

# 安全日志
security_logger = logging.getLogger('auto_coding.security')

# 允许的基础路径（防止路径遍历）
ALLOWED_BASE_PATHS = [
    os.path.expanduser("~/.enhance-claw"),
    "/tmp/auto-coding-projects",
    "/tmp",
]

# 最大输入长度
MAX_INPUT_LENGTH = 10000

# 危险模式（用于检测恶意输入）
DANGEROUS_PATTERNS = [
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__\s*\(',
    r'subprocess\.',
    r'os\.system\s*\(',
    r'open\s*\([\'\"]?/',  # 打开绝对路径
    r'\.\./',  # 路径遍历
    r'\$\{',  # 变量注入
    r'\$\(',  # 命令替换
    r';\s*rm\s',  # 命令链
    r'\|\s*rm\s',  # 管道攻击
]


# =============================================================================
# 路径安全验证
# =============================================================================

def validate_path(path: str, allowed_bases: List[str] = None) -> Tuple[bool, str]:
    """
    验证路径是否在允许范围内（防止路径遍历攻击）
    
    Args:
        path: 要验证的路径
        allowed_bases: 允许的基础路径列表（默认使用 ALLOWED_BASE_PATHS）
    
    Returns:
        (is_valid, reason_if_invalid)
    """
    if not path or not path.strip():
        return False, "空路径"
    
    # 规范化路径
    try:
        abs_path = os.path.abspath(os.path.expanduser(path))
    except Exception as e:
        return False, f"路径格式错误: {e}"
    
    # 检查路径遍历
    if '..' in path:
        security_logger.warning(f"[SECURITY] 检测到路径遍历尝试: {path}")
        return False, "路径包含非法的遍历字符 '..'"
    
    # 检查符号链接
    try:
        real_path = os.path.realpath(abs_path)
        if real_path != abs_path:
            security_logger.info(f"[SECURITY] 检测到符号链接: {path} -> {real_path}")
    except Exception as e:
        return False, f"无法解析符号链接: {e}"
    
    # 检查是否在允许的基础路径内
    bases = allowed_bases or ALLOWED_BASE_PATHS
    for base in bases:
        base_abs = os.path.abspath(os.path.expanduser(base))
        if abs_path.startswith(base_abs) or real_path.startswith(base_abs):
            return True, ""
    
    security_logger.warning(f"[SECURITY] 路径不在允许范围内: {abs_path}")
    return False, f"路径不在允许的目录内: {bases}"


def sanitize_path(path: str) -> str:
    """
    清洗路径，移除危险字符
    
    Args:
        path: 原始路径
    
    Returns:
        清洗后的路径
    """
    if not path:
        return ""
    
    # 移除路径遍历
    path = path.replace('..', '')
    
    # 移除空字节
    path = path.replace('\x00', '')
    
    # 移除控制字符
    path = re.sub(r'[\x00-\x1f\x7f]', '', path)
    
    return path.strip()


# =============================================================================
# 输入安全验证
# =============================================================================

def validate_input(text: str, max_length: int = None) -> Tuple[bool, str]:
    """
    验证用户输入是否安全
    
    Args:
        text: 用户输入
        max_length: 最大长度（默认使用 MAX_INPUT_LENGTH）
    
    Returns:
        (is_valid, reason_if_invalid)
    """
    if not text:
        return True, ""
    
    max_len = max_length or MAX_INPUT_LENGTH
    
    # 长度检查
    if len(text) > max_len:
        return False, f"输入过长（最大 {max_len} 字符）"
    
    # 危险模式检查
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            security_logger.warning(f"[SECURITY] 检测到危险模式: {pattern}")
            return False, f"输入包含危险模式"
    
    return True, ""


def sanitize_input(text: str, max_length: int = None) -> str:
    """
    清洗用户输入
    
    Args:
        text: 原始输入
        max_length: 最大长度
    
    Returns:
        清洗后的输入
    """
    if not text:
        return ""
    
    max_len = max_length or MAX_INPUT_LENGTH
    
    # 移除控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # 限制长度
    text = text[:max_len]
    
    return text.strip()


def detect_sensitive_info(text: str) -> List[Dict[str, str]]:
    """
    检测文本中的敏感信息
    
    Args:
        text: 要检测的文本
    
    Returns:
        检测到的敏感信息列表
    """
    sensitive_patterns = [
        (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[\w-]{20,}', 'API Key'),
        (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']+', 'Password'),
        (r'(?i)(secret|token)\s*[=:]\s*["\']?[\w-]{20,}', 'Secret/Token'),
        (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key'),
        (r'AKIA[A-Z0-9]{16}', 'AWS Access Key'),
        (r'eyJ[a-zA-Z0-9-_=]+\.[a-zA-Z0-9-_=]+\.[a-zA-Z0-9-_.+/=]*', 'JWT Token'),
    ]
    
    findings = []
    for pattern, info_type in sensitive_patterns:
        matches = re.findall(pattern, text)
        if matches:
            findings.append({
                'type': info_type,
                'count': len(matches),
                'pattern': pattern
            })
            security_logger.warning(f"[SECURITY] 检测到敏感信息: {info_type}")
    
    return findings


# =============================================================================
# 命令白名单 (参考 Claude Quickstarts)
# =============================================================================

# 允许的命令集合
ALLOWED_COMMANDS = {
    # 文件检查
    "ls", "cat", "head", "tail", "wc", "grep", "find", "tree",
    # 文件操作
    "cp", "mkdir", "chmod", "touch", "mv", "rm", "rmdir",
    # 目录
    "pwd", "cd",
    # Node.js
    "npm", "npx", "node", "yarn", "pnpm",
    # Python
    "pip", "pip3", "python", "python3", "pytest", "unittest", "poetry",
    # 版本控制
    "git",
    # 进程管理
    "ps", "lsof", "sleep", "pkill", "kill", "pgrep",
    # 构建工具
    "make", "cmake", "webpack", "vite", "rollup", "tsc",
    # 系统信息
    "uname", "whoami", "echo", "date", "time",
    # 网络命令已移除 (减少安全风险)
    # "curl", "wget",  # Removed - not needed for coding tasks
    # 文本编辑
    "sed", "awk",
}

# 需要额外验证的命令
COMMANDS_NEEDING_EXTRA_VALIDATION = {
    "pkill": {
        "allowed_targets": {"node", "npm", "npx", "python", "python3", "vite", "next", "webpack"},
        "description": "只允许杀死开发进程"
    },
    "kill": {
        "allowed_targets": {"node", "npm", "npx", "python", "python3", "vite", "next", "webpack"},
        "description": "只允许杀死开发进程"
    },
    "chmod": {
        "allowed_modes": {"+x", "u+x", "g+x", "o+x", "a+x", "-x"},
        "description": "只允许修改执行权限"
    },
    "rm": {
        "blocked_patterns": ["-rf", "-fr", "--force -recursive"],
        "description": "禁止强制递归删除"
    },
    "curl": {
        "blocked_patterns": ["-o", "--output", "|", ">", ">>"],
        "description": "禁止直接写入文件"
    },
    "wget": {
        "blocked_patterns": ["-O", "--output-document", "|", ">", ">>"],
        "description": "禁止直接写入文件"
    },
}

# 完全禁止的命令
BLOCKED_COMMANDS = {
    "sudo": "禁止提权操作",
    "su": "禁止切换用户",
    "dd": "禁止底层磁盘操作",
    "mkfs": "禁止格式化操作",
    "fdisk": "禁止分区操作",
    "mount": "禁止挂载操作",
    "umount": "禁止卸载操作",
    "iptables": "禁止防火墙配置",
    "ufw": "禁止防火墙配置",
    "systemctl": "禁止系统服务管理",
    "service": "禁止系统服务管理",
    "crontab": "禁止定时任务配置",
    "passwd": "禁止密码修改",
    "useradd": "禁止用户管理",
    "userdel": "禁止用户管理",
    "usermod": "禁止用户管理",
    "visudo": "禁止 sudo 配置",
}


# =============================================================================
# 命令验证函数
# =============================================================================

def split_command_segments(command_string: str) -> List[str]:
    """
    分割复合命令为独立命令段
    处理 && || ; 但不处理管道 (管道视为单个命令)
    """
    segments = re.split(r'\s*(?:&&|\|\|)\s*', command_string)
    result = []
    for segment in segments:
        sub_segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', segment)
        for sub in sub_segments:
            sub = sub.strip()
            if sub:
                result.append(sub)
    return result


def extract_commands(command_string: str) -> List[str]:
    """
    从 shell 命令字符串中提取命令名称
    处理管道、命令链和子 shell
    """
    commands = []
    segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', command_string)
    
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        
        try:
            tokens = shlex.split(segment)
        except ValueError:
            # 格式错误，返回空列表 (安全失败)
            return []
        
        if not tokens:
            continue
        
        expect_command = True
        
        for token in tokens:
            if token in ("|", "||", "&&", "&"):
                expect_command = True
                continue
            
            if token in ("if", "then", "else", "elif", "fi", "for", "while", 
                        "until", "do", "done", "case", "esac", "in", "!", 
                        "{", "}", "(", ")"):
                continue
            
            if token.startswith("-"):
                continue
            
            if "=" in token and not token.startswith("="):
                continue
            
            if expect_command:
                cmd = token.split("/")[-1]  # 处理路径
                commands.append(cmd)
                expect_command = False
    
    return commands


def validate_pkill_command(command_string: str) -> Tuple[bool, str]:
    """验证 pkill/kill 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("pkill")
    allowed_process_names = config["allowed_targets"]
    
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "无法解析 pkill 命令"
    
    if not tokens:
        return False, "空命令"
    
    args = []
    for token in tokens[1:]:
        if not token.startswith("-"):
            args.append(token)
    
    if not args:
        return False, "pkill 需要进程名称"
    
    target = args[-1]
    
    if " " in target:
        target = target.split()[0]
    
    if target in allowed_process_names:
        return True, ""
    return False, f"pkill 只允许用于开发进程：{allowed_process_names}"


def validate_chmod_command(command_string: str) -> Tuple[bool, str]:
    """验证 chmod 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("chmod")
    allowed_modes = config["allowed_modes"]
    
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "无法解析 chmod 命令"
    
    if not tokens or tokens[0] != "chmod":
        return False, "不是 chmod 命令"
    
    mode = None
    files = []
    
    for token in tokens[1:]:
        if token.startswith("-"):
            return False, "chmod 不支持标志"
        elif mode is None:
            mode = token
        else:
            files.append(token)
    
    if mode is None:
        return False, "chmod 需要模式参数"
    
    if not files:
        return False, "chmod 需要文件参数"
    
    if mode not in allowed_modes:
        return False, f"chmod 只允许模式：{allowed_modes}"
    
    return True, ""


def validate_rm_command(command_string: str) -> Tuple[bool, str]:
    """验证 rm 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("rm")
    blocked_patterns = config["blocked_patterns"]
    
    for pattern in blocked_patterns:
        if pattern in command_string:
            return False, f"rm 禁止使用模式：{pattern}"
    
    return True, ""


def validate_curl_command(command_string: str) -> Tuple[bool, str]:
    """验证 curl 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("curl")
    blocked_patterns = config["blocked_patterns"]
    
    for pattern in blocked_patterns:
        if pattern in command_string:
            return False, f"curl 禁止使用模式：{pattern}"
    
    return True, ""


def validate_wget_command(command_string: str) -> Tuple[bool, str]:
    """验证 wget 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("wget")
    blocked_patterns = config["blocked_patterns"]
    
    for pattern in blocked_patterns:
        if pattern in command_string:
            return False, f"wget 禁止使用模式：{pattern}"
    
    return True, ""


async def validate_command(command: str) -> Tuple[bool, str]:
    """
    验证命令是否允许
    
    Returns:
        (is_allowed, reason_if_blocked)
    """
    if not command or not command.strip():
        return False, "空命令"
    
    # 检查完全禁止的命令
    commands = extract_commands(command)
    if not commands:
        return False, "无法解析命令"
    
    for cmd in commands:
        if cmd in BLOCKED_COMMANDS:
            return False, f"禁止的命令 '{cmd}': {BLOCKED_COMMANDS[cmd]}"
    
    # 白名单检查
    for cmd in commands:
        if cmd not in ALLOWED_COMMANDS:
            return False, f"命令 '{cmd}' 不在白名单中"
    
    # 分割命令段进行额外验证
    segments = split_command_segments(command)
    
    # 额外验证敏感命令
    for cmd in commands:
        if cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
            cmd_segment = command  # 简化处理，使用完整命令
            
            if cmd in ("pkill", "kill"):
                allowed, reason = validate_pkill_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "chmod":
                allowed, reason = validate_chmod_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "rm":
                allowed, reason = validate_rm_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "curl":
                allowed, reason = validate_curl_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "wget":
                allowed, reason = validate_wget_command(cmd_segment)
                if not allowed:
                    return False, reason
    
    return True, ""


def get_security_report() -> Dict[str, Any]:
    """获取安全配置报告"""
    return {
        "allowed_commands_count": len(ALLOWED_COMMANDS),
        "blocked_commands_count": len(BLOCKED_COMMANDS),
        "extra_validation_count": len(COMMANDS_NEEDING_EXTRA_VALIDATION),
        "allowed_commands": sorted(list(ALLOWED_COMMANDS)),
        "blocked_commands": {k: v for k, v in BLOCKED_COMMANDS.items()},
    }


# =============================================================================
# 测试代码
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("运行 Security 测试...\n")
    
    async def run_tests():
        test_cases = [
            # (command, should_allow, description)
            ("ls -la", True, "基本文件查看"),
            ("cat file.txt", True, "读取文件"),
            ("git status", True, "Git 操作"),
            ("npm install", True, "NPM 安装"),
            ("python3 app.py", True, "Python 运行"),
            ("mkdir test", True, "创建目录"),
            ("chmod +x script.sh", True, "添加执行权限"),
            ("pkill node", True, "杀死 node 进程"),
            
            ("sudo rm -rf /", False, "提权删除"),
            ("rm -rf /", False, "递归强制删除"),
            ("pkill sshd", False, "杀死非开发进程"),
            ("dd if=/dev/zero", False, "磁盘操作"),
            ("mkfs.ext4 /dev/sda", False, "格式化"),
            ("unknown_command", False, "未知命令"),
            ("curl http://example.com -o file.txt", False, "curl 写入文件"),
        ]
        
        passed = 0
        failed = 0
        
        for command, should_allow, description in test_cases:
            allowed, reason = await validate_command(command)
            
            if allowed == should_allow:
                print(f"✅ {description}: {command}")
                passed += 1
            else:
                print(f"❌ {description}: {command}")
                print(f"   期望：{'允许' if should_allow else '禁止'}, 实际：{'允许' if allowed else '禁止'}")
                if reason:
                    print(f"   原因：{reason}")
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"通过：{passed}/{len(test_cases)}")
        print(f"失败：{failed}/{len(test_cases)}")
        
        if failed == 0:
            print("\n🎉 所有 Security 测试通过!")
        else:
            print(f"\n⚠️  有 {failed} 个测试失败")
        
        return failed == 0
    
    # 运行测试
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
