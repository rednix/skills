---
name: skill-maker
description: 用于根据对话记忆提炼可复用工作流并生成高质量 SKILL.md，适用于“从聊天沉淀方法论”“把一次性操作升级为可复用技能”场景。
metadata:
  openclaw:
    emoji: "🧩"
---

# Skill Maker 使用说明

## Trigger
['创建skill', '新建技能', '写SKILL.md', '根据对话生成skill', '从聊天沉淀工作流', '技能抽取', 'skill-maker', '自动查找上下文生成skill']

## 使用说明
1. 触发方式：当用户表达“从对话生成技能/沉淀工作流/写 SKILL.md”时调用本技能。  
2. 输入建议：至少提供以下三项中的两项  
   - 任务主题关键词（如“会议纪要”“周报生成”）  
   - 时间范围（如“最近 7 天对话”）  
   - 来源范围（如“聊天记录 + 当前项目文件”）  
3. 自动模式：未提供完整对话时，先自动检索上下文，再进行筛选和提炼。  
4. 输出结果：产出可直接落地的 `SKILL.md` 草稿，并附上 skill 名称、触发词、适用边界与使用示例。  
5. 失败兜底：若上下文不足，先返回“缺失信息清单”，再请求补充最小必要信息。
6. 输出路径规范：默认写入 `~/.openclaw/skills/<skill-name>/SKILL.md`；不要写到 `~/.openclaw/workspace/skills`。

## Procedure
1. 收集输入对话记忆：支持两种方式  
   - 手动模式：用户直接提供对话片段  
   - 自动模式：根据任务关键词自动检索最近会话、相关文件、历史草稿中的上下文  
2. 自动模式上下文筛选：优先保留“目标、约束、偏好、操作步骤、产出格式、复盘经验”，剔除纯寒暄、重复信息与无关片段。  
3. 判断是否值得沉淀为技能：仅当任务具备“可重复、可迁移、可验收”特征时创建 skill；纯一次性需求不沉淀。  
4. 提炼任务主线：将对话中的零散动作归并为稳定流程，抽象为 4-8 个可执行步骤，避免写成具体项目细节。  
5. 生成技能元信息：  
   - `name` 使用小写英文加连字符（如 `weekly-report-maker`）  
   - `description` 同时说明“解决什么问题 + 适用场景”  
   - `trigger` 覆盖用户常见口语表达和同义词  
6. 生成 SKILL.md 主体：按固定结构输出 `Trigger / Procedure / Experience / User Preferences / Examples`，必要时补充 `Tool Usage` 和 `Additional Information`。  
7. 进行去敏与通用化处理：移除人名、账号、路径、密钥、内部代号等敏感信息；将具体业务词替换为通用表达。  
8. 质量验收：检查“可执行性、可复用性、可读性、可调用性”，确保新 skill 可直接用于后续任务。  
9. 输出生成结果：给出 skill 存放路径与简要使用说明，便于立即调用。
10. 路径校验：若检测到输出在 `workspace/skills`，立即迁移到 `~/.openclaw/skills` 并告知最终路径。

## Experience
1. 先做“是否值得沉淀”的筛选，再写技能，能显著减少低价值 skill。  
2. Procedure 应描述稳定方法论，不要绑定单次任务的对象和数据。  
3. 示例必须接近最终交付形态，优先给可直接复用的 markdown 模板。  
4. Trigger 要覆盖用户自然语言说法，否则技能很难被命中。  
5. 先通用化再美化表达，通常能提升 skill 的长期复用率。

## User Preferences
- 偏好结构化输出，章节稳定、可直接复用。  
- 优先产出最小可用版本（MVP），再迭代补充参考资料。  
- 解释要简洁，重点体现“怎么做”而不是“为什么很重要”。  
- 能用清单表达的内容尽量清单化，便于执行和检查。

## Examples

### 示例：自动提炼面试评估技能

- 任务描述：从面试对话记录中提炼可复用评估技能。  
- 输入：最近 7 天面试对话 + 目标岗位关键词。  
- 输出：结构化 `SKILL.md` 草稿。  

示例输出结构：

    ---
    name: interview-summary-maker
    description: 用于从面试对话记录中提炼结构化总结，适用于候选人评估、复盘和团队同步场景。
    ---
    ## Trigger
    ['面试总结', '候选人复盘', '生成评估报告']
    ## Procedure
    1. 收集并合并面试对话记录
    2. 提炼维度（沟通、技术、经验匹配、风险）
    3. 将主观评价转为证据化描述
    4. 生成结构化结论与建议

## Tool Usage
文本编辑器、知识库文档平台、会话日志检索工具（如历史消息检索、笔记系统）均可。

## Additional Information

### 标准 SKILL.md 格式规范（参考 browser-scrape）
- 必须包含 frontmatter：`name`、`description`，可选 `metadata.openclaw.emoji`  
- 建议固定章节顺序：`Trigger -> 使用说明/推荐流程 -> Experience -> User Preferences -> Examples -> Tool Usage -> Additional Information`  
- `Trigger` 需覆盖口语化关键词，避免只写技术术语  
- `Procedure/推荐流程` 每步应可执行，避免抽象原则堆叠  
- `Examples` 需包含“输入-输出”或完整 markdown 产出模板  
- 有外部文档时，使用 `See also` 链接到 `./reference/reference.md`

### 自动模式输入建议
- 指定主题关键词：例如“会议纪要整理”“周报生成”“需求评审”  
- 指定时间范围：例如“最近 7 天对话”  
- 指定来源范围：例如“聊天记录 + 当前项目相关文件”  
- 指定输出名称：例如 `meeting-recap-maker`

### 是否值得创建 skill（快速判定）
- 该任务是否会重复出现至少 3 次  
- 是否存在稳定输入、稳定步骤和稳定输出  
- 他人是否可以按该 skill 独立执行

### SKILL.md 质量检查清单
- 名称是否为小写英文加连字符（如 `skill-maker`）  
- description 是否包含“能力 + 场景 + 边界”  
- Trigger 是否覆盖口语化表达和同义词  
- Procedure 是否可执行且有顺序依赖  
- Experience 是否是跨场景经验而非单次复盘  
- 示例是否展示完整输出结构且可复用  
- 是否完成去敏处理（人名、账号、路径、密钥）

## See also

- [reference/reference.md](./reference/reference.md) — 自动上下文检索、技能提炼规则与标准产出模板。