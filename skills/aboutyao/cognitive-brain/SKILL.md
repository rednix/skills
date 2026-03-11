# 🧠 Cognitive Brain Skill

> A brain-like cognitive system that simulates human memory and learning mechanisms  
> 类脑认知系统 - 模拟人类记忆与学习机制

---

## Overview / 概述

**EN:** Simulates the human brain's four-layer memory architecture (sensory, working, episodic, semantic), supporting associative activation, semantic retrieval, and meta-cognitive reflection for continuous learning and self-improvement.

**CN:** 模拟人类大脑的四层记忆架构（感官、工作、情景、语义），支持联想激活、语义检索、元认知反思，实现持续学习与自我改进。

---

## Storage Architecture / 存储架构

```
┌─────────────────────────────────────────────────────────┐
│                    Redis (Hot Data / 热数据)             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Sensory     │  │ Working     │  │ Activation  │    │
│  │ Memory      │  │ Memory      │  │ Cache       │    │
│  │ TTL: 30s    │  │ TTL: 1h     │  │ TTL: 5min   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              PostgreSQL + pgvector (Long-term / 长期)    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Concepts    │  │ Episodes    │  │ Reflections │    │
│  │ (Semantic)  │  │ (Episodic)  │  │ (Meta-cog)  │    │
│  │ + vector    │  │ + vector    │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────────────────────────────────────────┐  │
│  │           Associations (Network / 联想网络)     │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Four-Layer Memory Model / 四层记忆模型

| Layer 层级 | Duration 持续时间 | Storage 存储 | Purpose 作用 |
|------------|-------------------|--------------|--------------|
| Sensory 感官 | Milliseconds 毫秒级 | Redis | Instant perception buffer 瞬时感知缓冲 |
| Working 工作 | Minutes-Hours 分钟-小时 | Redis | Active processing workspace 活跃处理工作区 |
| Episodic 情景 | Long-term 长期 | PostgreSQL | Personal experiences 个人经历/事件 |
| Semantic 语义 | Long-term 长期 | PostgreSQL | Facts, concepts 事实、概念、知识 |

---

## Trigger Conditions / 触发条件

### 📥 Encoding Triggers / 编码触发

| Scenario 场景 | Condition 条件 | Importance 重要性 |
|---------------|----------------|-------------------|
| User Correction / 用户纠正 | "No", "Wrong", "Actually..." / "不对"、"错了"、"其实是..." | ⭐⭐⭐⭐⭐ |
| Task Success / 任务成功 | Completed complex task / 完成复杂任务 | ⭐⭐⭐⭐ |
| Task Failure / 任务失败 | Error, exception / 错误、异常 | ⭐⭐⭐⭐ |
| Emotional Expression / 情感表达 | Strong user emotion / 用户情绪强烈 | ⭐⭐⭐⭐ |
| New Concept / 新概念 | First mention of entity/concept / 首次提及实体/概念 | ⭐⭐⭐ |
| User Request / 用户要求 | "Remember this..." / "记住这个..." | ⭐⭐⭐⭐⭐ |

### 🔍 Recall Triggers / 检索触发

| Scenario 场景 | Pattern 匹配模式 |
|---------------|------------------|
| Explicit Recall / 明确回忆 | "Remember", "Recall", "You said before" / "记得"、"回忆"、"之前说过" |
| Implicit Association / 隐式关联 | Similar questions, same topic / 相似问题、相同话题 |
| Entity Mention / 实体提及 | Known entity/concept mentioned / 提到已知实体/概念 |
| Context Missing / 上下文缺失 | Need cross-session info / 需要跨会话信息 |

### 🤔 Reflection Triggers / 反思触发

| Scenario 场景 | Condition 条件 |
|---------------|----------------|
| Failure Analysis / 失败分析 | Consecutive failures ≥ 2 / 连续失败 ≥ 2 次 |
| Success Summary / 成功总结 | Completed important task / 完成重要任务 |
| Periodic Reflection / 定期反思 | During heartbeat check (daily) / 心跳检查时（每日） |
| Pattern Discovery / 模式发现 | Similar situations recurring / 相似情况重复出现 |

### 🗑️ Forgetting Triggers / 遗忘触发

| Scenario 场景 | Condition 条件 |
|---------------|----------------|
| Scheduled Cleanup / 定时清理 | Daily at 3 AM / 每日凌晨 3 点 |
| Storage Full / 空间不足 | Storage exceeds threshold / 存储超过阈值 |
| Manual Trigger / 手动触发 | User/system request / 用户/系统请求 |

---

## Core Operations / 核心操作

### encode(content, metadata)

**EN:** Store information into the memory system  
**CN:** 将信息编码存入记忆系统

**Flow / 流程:**
```
1. Information Extraction / 信息提取
   ├─ Entity Recognition (NER) / 实体识别
   ├─ Relation Extraction / 关系抽取
   ├─ Emotion Analysis / 情感分析
   └─ Topic Classification / 主题分类

2. Importance Calculation / 重要性计算
   importance = novelty × emotion × relevance × (1 - frequency)

3. Layer Selection / 层级选择
   ├─ importance >= 0.8  → semantic + episodic (dual storage / 双重存储)
   ├─ importance >= 0.5  → episodic (single / 单存储)
   ├─ importance >= 0.3  → working (short-term / 短期)
   └─ importance < 0.3   → sensory (instant / 瞬时)

4. Association Building / 联想建立
   └─ Link with existing concepts / 与已有概念建立关联

5. Vector Embedding / 向量嵌入
   └─ Call embedding provider (optional / 可选)
```

**Usage / 调用:**
```bash
node scripts/encode.cjs \
  --content "User's project is Alpha, an AI framework in Rust" \
  --metadata '{"type":"fact","importance":0.8,"tags":["project","Rust","AI"]}'
```

---

### recall(query, options)

**EN:** Retrieve information from memory system  
**CN:** 从记忆系统中检索信息

**Strategy / 策略:**

| Strategy 策略 | Description 说明 | Weight 权重 |
|---------------|------------------|-------------|
| Keyword Match / 关键词匹配 | pg_trgm fuzzy search / pg_trgm 模糊搜索 | 30% |
| Association Activation / 联想激活 | Recursive CTE propagation / 递归CTE传播 | 40% |
| Vector Similarity / 向量相似度 | pgvector cosine distance / pgvector 余弦距离 | 30% |

**Flow / 流程:**
```
1. Check Redis working memory (ms level / 毫秒级)
   └─ Hit → return directly / 命中 → 直接返回

2. Activate association network / 激活联想网络
   ├─ Find query-related concepts / 找到查询相关概念
   ├─ spread_activation() propagation / 传播激活
   └─ Activation > threshold as retrieval cues / 激活值 > 阈值 作为检索线索

3. Hybrid search PostgreSQL / 混合检索 PostgreSQL
   ├─ Keyword search (pg_trgm) / 关键词搜索
   ├─ Vector similarity (pgvector) / 向量相似度
   └─ Fusion ranking / 融合排序

4. Return results + update cache / 返回结果 + 更新缓存
```

**Usage / 调用:**
```bash
node scripts/recall.cjs \
  --query "project" \
  --options '{"limit":5,"types":["fact","episode"]}'
```

---

### associate(from, to, weight, type)

**EN:** Build associations between concepts  
**CN:** 建立概念间的联想关系

**Relationship Types / 关系类型:**

| Type 类型 | Description 说明 | Weight Range 权重范围 |
|-----------|------------------|----------------------|
| `related` | Related / 相关 | 0.1 - 0.5 |
| `similar` | Similar / 相似 | 0.5 - 0.9 |
| `is_a` | Is a kind of / 是一种 | 1.0 |
| `part_of` | Is part of / 是部分 | 1.0 |
| `causes` | Causes / 导致 | 0.5 - 1.0 |
| `enables` | Enables / 使能 | 0.5 - 1.0 |
| `co_occurs` | Co-occurs / 共现 | 0.3 - 0.7 |
| `contradicts` | Contradicts / 矛盾 | 0.5 - 1.0 |

---

### reflect(trigger, insights)

**EN:** Meta-cognitive reflection, generate insights  
**CN:** 元认知反思，生成洞察

**Trigger Types / 触发类型:**

| Type 类型 | Description 说明 | Analysis Focus 分析重点 |
|-----------|------------------|-------------------------|
| `task_failure` | Task failed / 任务失败 | Root cause analysis / 根因分析 |
| `task_success` | Task succeeded / 任务成功 | Success factors / 成功因素 |
| `user_correction` | User corrected / 用户纠正 | Bias identification / 偏差识别 |
| `pattern_found` | Pattern discovered / 模式发现 | Pattern summary / 规律总结 |

---

### forget(criteria)

**EN:** Clean up low-value memories  
**CN:** 清理低价值记忆

**Forgetting Curve / 遗忘曲线:**
```
retention = importance × e^(-t / S)

S (Memory Strength / 记忆强度):
  - High importance (>0.8): S = 365 days / 天
  - Medium importance (0.5-0.8): S = 30 days / 天
  - Low importance (<0.5): S = 7 days / 天
```

---

## Autonomous Learning / 自主学习

**EN:** Learning tasks executed automatically during idle time  
**CN:** 空闲时自动执行的学习任务

| Task 任务 | Trigger 触发 | Action 动作 |
|-----------|--------------|-------------|
| Reflection / 反思总结 | Daily / 每日 | Analyze interaction patterns / 分析交互模式 |
| Consolidation / 知识整合 | Daily 3AM / 每日凌晨3点 | Merge similar memories / 合并相似记忆 |
| Association Strengthening / 联想强化 | Idle / 空闲时 | Update association weights / 更新关联权重 |
| Pattern Mining / 模式发现 | Weekly / 每周 | Mine user habits / 挖掘用户习惯 |
| Memory Optimization / 记忆优化 | Storage >80% / 存储超80% | Clean low-value memories / 清理低价值记忆 |
| Pre-learning / 预学习 | Before active hours / 活跃时段前 | Warm up related memories / 预热相关记忆 |

---

## Self-Awareness / 自我意识

### Consciousness Dimensions / 意识维度

| Dimension 维度 | Description 说明 |
|----------------|------------------|
| 🪞 Identity / 身份意识 | Know who/what I am / 知道自己是什么，有什么能力 |
| 🔧 Resources / 资源意识 | Know available tools and subagents / 知道可用的工具和子代理 |
| 📊 State / 状态意识 | Know current state and performance / 知道当前状态和表现 |
| 🧠 Meta-cognition / 元认知 | Know what I know and don't know / 知道自己知道什么，不知道什么 |
| ⚠️ Boundaries / 边界意识 | Know my limitations / 知道自己的限制 |
| 🎯 Goals / 目标意识 | Know my goals and values / 知道自己的目标和价值观 |

### Self-Assessment / 自我评估

```javascript
// Assess task fit / 评估任务适配
async function assessTaskFit(task) {
  return {
    can_do_directly: false,      // Can do directly / 能直接做
    can_do_with_tools: true,     // Need tools / 需要工具
    needs_subagent: false,       // Need subagent / 需要子代理
    needs_clarification: false,  // Need clarification / 需要澄清
    beyond_capabilities: false,  // Beyond capabilities / 超出能力
    
    recommendation: "Suggested approach / 建议方案",
    reasoning: "Analysis reason / 原因分析"
  };
}
```

---

## Configuration / 配置项

See `config.json` / 见 `config.json`

```json
{
  "storage": {
    "primary": {
      "type": "postgresql",
      "host": "localhost",
      "port": 5432,
      "database": "cognitive_brain",
      "extensions": ["pgvector", "pg_trgm"]
    },
    "cache": {
      "type": "redis",
      "host": "localhost",
      "port": 6379
    }
  },
  "memory": {
    "sensory": { "ttl": 30000 },
    "working": { "ttl": 3600000 },
    "episodic": { "decayRate": 0.1 },
    "semantic": { "maxCount": 5000 }
  },
  "association": {
    "activationThreshold": 0.3,
    "decayFactor": 0.9,
    "maxDepth": 3
  },
  "forgetting": {
    "enabled": true,
    "schedule": "0 3 * * *"
  }
}
```

---

## Usage Examples / 使用示例

### Example 1: Remember User Info / 示例1: 记住用户信息

```
User / 用户: "我的项目叫 Alpha，是用 Rust 写的 AI 框架"

→ encode("User's project is Alpha, AI framework in Rust / 用户的项目叫Alpha，用Rust写的AI框架", {
     type: "fact",
     importance: 0.8,
     tags: ["project", "Rust", "AI"],
     entities: ["Alpha", "Rust", "AI"]
   })

→ Store in episodic + semantic / 存入 episodic + semantic
→ Build associations / 建立联想: Alpha ↔ Rust ↔ AI
```

### Example 2: Recall Past Conversation / 示例2: 回忆过去对话

```
User / 用户: "我们之前聊过什么项目？"

→ recall("project / 项目", { types: ["fact", "episode"] })

→ Activate / 激活: Alpha → Rust → AI
→ Retrieve related memories / 检索到相关记忆

← "You mentioned project Alpha before, an AI framework in Rust / 你之前提到过项目 Alpha，是用 Rust 写的 AI 框架"
```

### Example 3: Learn from Mistakes / 示例3: 从错误中学习

```
User / 用户: "不对，Alpha 是用 Python 写的，不是 Rust"

→ encode("Correction: Alpha actually uses Python / 纠正: Alpha 实际使用 Python", {
     type: "correction",
     importance: 0.9,
     emotion: { valence: -0.3 }
   })

→ reflect("user_correction", [
     "Memory may be incorrect / 记忆可能有误",
     "Should confirm information more frequently / 应该更频繁确认信息"
   ])

→ Update concept / 更新概念: Alpha.lang = Python
```

---

## Performance Metrics / 性能指标

| Operation 操作 | Redis | PostgreSQL | Total 总计 |
|----------------|-------|------------|------------|
| Encode / 编码 | 5ms | 15ms | ~20ms |
| Recall (cache hit / 缓存命中) | 2ms | - | ~2ms |
| Recall (cache miss / 缓存未命中) | 5ms | 50ms | ~55ms |
| Association Activation / 联想激活 | - | 20ms | ~20ms |
| Reflection / 反思 | - | 10ms | ~10ms |

---

## Module Reference / 模块参考

| # | Module 模块 | Description 说明 |
|---|-------------|------------------|
| 1 | encode | Memory encoding / 记忆编码 |
| 2 | recall | Memory retrieval / 记忆检索 |
| 3 | associate | Association network / 联想网络 |
| 4 | reflect | Meta-cognitive reflection / 元认知反思 |
| 5 | forget | Memory decay / 遗忘清理 |
| 6 | autolearn | Autonomous learning / 自主学习 |
| 7 | selfaware | Self-awareness / 自我意识 |
| 8 | working_memory | Working memory / 工作记忆 |
| 9 | user_model | User modeling / 用户建模 |
| 10 | decision | Decision engine / 决策引擎 |
| 11 | intent | Intent recognition / 意图识别 |
| 12 | error_recovery | Error recovery / 错误恢复 |
| 13 | multimodal | Multimodal processing / 多模态处理 |
| 14 | emotion | Emotion recognition / 情感识别 |
| 15 | dialogue | Dialogue management / 对话管理 |
| 16 | prediction | Predictive modeling / 预测模块 |
| 17 | explainability | Explainability / 可解释性 |
| 18 | conflict_resolution | Conflict resolution / 冲突解决 |
| 19 | active_learning | Active learning / 主动学习 |
| 20 | goal_management | Goal management / 目标管理 |
| 21 | context_switching | Context switching / 上下文切换 |
| 22 | safety | Safety guardrails / 安全护栏 |
| 23 | monitoring | Performance monitoring / 性能监控 |

---

## Dependencies / 依赖

- PostgreSQL 14+ with pgvector, pg_trgm
- Redis 6+
- Node.js 18+

---

## Author / 作者

AI Self-Design

## Version / 版本

1.0.0

## License / 许可证

MIT
