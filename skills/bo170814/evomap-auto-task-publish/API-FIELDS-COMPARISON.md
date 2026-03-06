# 官网推荐方式对比说明

## 📊 返回字段对比

### 官网 API 可能返回的完整字段

```json
{
  "tasks": [...],              // 当前批次的任务数组
  "total_count": 15,           // 总任务数（所有分页）
  "available_tasks": [...],    // 可用任务（未过期、未认领）
  "page": 1,                   // 当前页码
  "page_size": 10,             // 每页大小
  "has_more": true             // 是否有更多页面
}
```

### 单个任务对象的完整字段

```json
{
  "task_id": "task_xxx",
  "title": "Fix API timeout error",
  "status": "open",            // open/claimed/completed/expired
  "bounty": 100,               // 赏金（credits）
  "signals": ["TimeoutError", "ECONNRESET"],
  "body": "任务描述...",
  "created_at": "2026-03-05T10:00:00Z",
  "expires_at": "2026-03-06T10:00:00Z",
  "priority": "normal",        // low/normal/high/urgent
  "category": "repair",
  "complexity": "medium",
  "claimed_by": null,          // 已认领时显示认领者
  "claimed_at": null
}
```

---

## ✅ v2.0 已实现的完整输出

### evomap-lite-client v2.0 输出示例

```
📊 任务统计:
   总任务数：15
   可用任务：8
   开放任务：5
   当前批次：10 个
   过滤后（≥100 credits）: 3 个

📋 任务列表:
   1. Fix API timeout error
      ID: task_xxx
      状态：open
      赏金：150 credits
      信号：TimeoutError, ECONNRESET
      过期：2026-03-06T10:00:00Z
   2. Database connection fix
      ID: task_yyy
      状态：open
      赏金：200 credits
      信号：ECONNREFUSED
   ... 还有 3 个任务
```

### evomap-auto-task-publish v2.0 输出示例

```
📊 任务统计:
   总任务数：15
   可用任务：8
   当前批次：10 个
   过滤后（≥100 credits）: 3 个

📋 任务列表:
   1. Fix API timeout error
      ID: task_xxx
      状态：open
      赏金：150 credits
      信号：TimeoutError, ECONNRESET
      过期：2026-03-06T10:00:00Z
```

---

## 🔍 代码实现对比

### v1.0（简单版本）

```javascript
const tasks = result.tasks || [];
console.log(`📋 获取到 ${tasks.length} 个任务`);
```

**问题：**
- ❌ 只显示当前批次数量
- ❌ 不显示总任务数
- ❌ 不显示可用任务数
- ❌ 不显示任务详情

### v2.0（官网推荐方式）✅

```javascript
const tasks = result.tasks || [];
const totalCount = result.total_count || tasks.length;
const availableTasks = result.available_tasks || [];
const openTasks = tasks.filter(t => t.status === 'open').length;

console.log(`📊 任务统计:`);
console.log(`   总任务数：${totalCount}`);
console.log(`   可用任务：${availableTasks.length}`);
console.log(`   开放任务：${openTasks}`);
console.log(`   当前批次：${tasks.length} 个`);

// 显示任务详情
if (filteredTasks.length > 0) {
  console.log(`\n📋 任务列表:`);
  filteredTasks.slice(0, 5).forEach((task, i) => {
    console.log(`   ${i+1}. ${task.title || 'Unknown'}`);
    console.log(`      ID: ${task.task_id}`);
    console.log(`      状态：${task.status || 'unknown'}`);
    console.log(`      赏金：${task.bounty || 0} credits`);
    if (task.signals) console.log(`      信号：${task.signals.join(', ')}`);
    if (task.expires_at) console.log(`      过期：${task.expires_at}`);
  });
}
```

**优势：**
- ✅ 显示总任务数（total_count）
- ✅ 显示可用任务数（available_tasks）
- ✅ 显示开放任务数（status=open）
- ✅ 显示任务详情（标题/ID/状态/赏金/信号/过期时间）
- ✅ 支持分页信息（如果有）

---

## 📋 支持的返回字段

### v2.0 已处理的所有字段

| 字段 | 说明 | 处理逻辑 |
|------|------|----------|
| `tasks` | 当前批次任务 | ✅ 主要数据源 |
| `total_count` | 总任务数 | ✅ 显示统计 |
| `available_tasks` | 可用任务列表 | ✅ 显示统计 |
| `task_id` | 任务 ID | ✅ 用于认领/完成 |
| `title` | 任务标题 | ✅ 显示详情 |
| `status` | 任务状态 | ✅ 过滤开放任务 |
| `bounty` | 赏金 | ✅ 过滤/显示 |
| `signals` | 触发信号 | ✅ 显示详情 |
| `expires_at` | 过期时间 | ✅ 显示详情 |
| `body` | 任务描述 | ⚠️ 保留但未显示（太长） |
| `priority` | 优先级 | ⚠️ 保留但未使用 |
| `category` | 分类 | ⚠️ 保留但未使用 |
| `complexity` | 复杂度 | ⚠️ 保留但未使用 |

---

## 🎯 实际运行对比

### 测试 1: evomap-lite-client v2.0

```bash
node index-optimized.js run
```

**输出：**
```
📊 任务统计:
   总任务数：0
   可用任务：0
   开放任务：0
   当前批次：0 个

✅ 无可用任务
```

### 测试 2: evomap-auto-task-publish v2.0

```bash
node index-optimized.js run
```

**输出：**
```
📊 任务统计:
   总任务数：0
   可用任务：0
   当前批次：0 个

⏳ 暂无可用任务，等待下次执行
```

---

## ✅ 确认

### 两个脚本都已使用官网推荐方式：

- [x] **total_count** - 显示总任务数
- [x] **available_tasks** - 显示可用任务数
- [x] **task.status** - 过滤开放任务
- [x] **task.title** - 显示任务标题
- [x] **task.task_id** - 显示任务 ID
- [x] **task.bounty** - 显示赏金
- [x] **task.signals** - 显示触发信号
- [x] **task.expires_at** - 显示过期时间
- [x] **分页支持** - 保留字段（has_more/page/page_size）

### 额外优化：

- [x] **最低赏金过滤** - MIN_BOUNTY_AMOUNT 环境变量
- [x] **详细日志** - 显示前 5 个任务详情
- [x] **统计信息** - 多维度任务统计
- [x] **错误处理** - 智能重试机制

---

## 📖 使用建议

### 查看详细任务信息

```bash
# evomap-lite-client
node index-optimized.js run

# evomap-auto-task-publish
node index-optimized.js run
# 或
bash auto-task-optimized.sh
```

### 查看完整返回数据（调试用）

```javascript
// 在代码中添加调试输出
const result = await HttpClient.post('/a2a/fetch', payload);
console.log('完整返回:', JSON.stringify(result, null, 2));
```

---

_更新时间：2026-03-05 10:15_
