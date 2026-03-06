#!/bin/bash
# EvoMap 自动任务执行脚本 v2.0 - 优化版
# 流程：节点上线 → 获取任务 → 认领 → 发布 → 完成
# 日志文件：/tmp/evomap-task.log

set -e

# ============ 配置区 ============
LOG_FILE="/tmp/evomap-task.log"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTIFY_SCRIPT="$SKILL_DIR/notify.sh"

# Node.js 路径（自动检测）
if command -v node &> /dev/null; then
    NODE_PATH=$(which node)
elif [ -f "/root/.nvm/versions/node/v22.22.0/bin/node" ]; then
    NODE_PATH="/root/.nvm/versions/node/v22.22.0/bin/node"
else
    NODE_PATH="node"
fi

# 环境变量
export A2A_HUB_URL="${A2A_HUB_URL:-https://evomap.ai}"
export A2A_NODE_ID="${A2A_NODE_ID:-}"
export MIN_BOUNTY_AMOUNT="${MIN_BOUNTY_AMOUNT:-0}"

# ============ 日志函数 ============
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_header() {
    echo "" >> $LOG_FILE
    echo "========================================" >> $LOG_FILE
    log "INFO" "EvoMap 自动任务执行 v2.0"
    log "INFO" "执行时间：$(date)"
    echo "========================================" >> $LOG_FILE
}

# ============ 主流程 ============
log_header

cd "$SKILL_DIR"

log "INFO" "Node 路径：$NODE_PATH"
log "INFO" "技能目录：$SKILL_DIR"

# 步骤 1：运行优化后的客户端（自动完成所有步骤）
log "INFO" "【步骤 1】执行任务流程..."

result=$($NODE_PATH index-optimized.js run 2>&1)
echo "$result" >> $LOG_FILE

# 分析结果
if echo "$result" | grep -q "无可用任务\|无开放任务"; then
    log "INFO" "⏳ 暂无可用任务，等待下次执行"
    log "INFO" "STATUS: NO_TASKS"
    [ -x "$NOTIFY_SCRIPT" ] && bash "$NOTIFY_SCRIPT" "NO_TASKS" 2>/dev/null || true
    exit 0
fi

if echo "$result" | grep -q "✅ 本轮完成"; then
    log "INFO" "✅ 任务执行成功！"
    log "INFO" "STATUS: SUCCESS"
    [ -x "$NOTIFY_SCRIPT" ] && bash "$NOTIFY_SCRIPT" "SUCCESS" 2>/dev/null || true
    exit 0
fi

if echo "$result" | grep -q "❌ 执行出错"; then
    error_msg=$(echo "$result" | grep "❌ 执行出错" | cut -d':' -f2-)
    log "ERROR" "❌ 执行失败：$error_msg"
    log "INFO" "STATUS: EXEC_FAILED"
    [ -x "$NOTIFY_SCRIPT" ] && bash "$NOTIFY_SCRIPT" "EXEC_FAILED" "$error_msg" 2>/dev/null || true
    exit 1
fi

# 其他情况
log "WARN" "⚠️  未知执行状态"
log "INFO" "STATUS: UNKNOWN"
echo "$result" >> $LOG_FILE
[ -x "$NOTIFY_SCRIPT" ] && bash "$NOTIFY_SCRIPT" "UNKNOWN" 2>/dev/null || true
exit 0
