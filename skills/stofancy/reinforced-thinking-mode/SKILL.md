---
name: reinforced-thinking-mode
description: Multi-round independent deep thinking. Each round produces complete, final-quality solutions. Non-iterative, no TODOs, no angle constraints—pure divergent thinking.
---

# Reinforced Thinking Mode

## When to Use

Activate when user needs deep, multi-angle analysis:
- Keywords: "deep thinking", "multi-angle", "comprehensive evaluation", "design solution", "architecture planning"
- Intent: Complex system design, strategic decisions, innovation, risk assessment

**Complexity → Rounds:**
- Simple (factual, clear): 2-3 rounds
- Medium (feature design, trade-offs): 4-5 rounds
- Complex (architecture, strategy): 5-7 rounds
- Wicked (undefined, conflicting): 7-10 rounds

## Core Principle

**N independent, complete thinking sessions—not iterative refinement.**

Each round must be: *"If this were the last round, I am completely satisfied."*

### Mental Model

✅ **Think:** "This is my only chance—give it everything"

❌ **Never think:** "I'll improve this next round"

---

## Why File I/O Matters

Without writing files, AI "hallucinates" N rounds internally—generating summaries instead of truly thinking.

**File I/O enforces:**
- Fresh thinking each round (can't rely on memory)
- True independence (must read files)
- Verifiability (users see each round)

---

## Hard Constraints

### File Access
- **Each round reads ONLY:** `problem.md` + `round_{i-1}.md` (Round 1: only problem.md)
- **Never** read other rounds' details

### Forbidden Words
Never use in solution files: `TODO`, `to be improved`, `next round`, `later`, `refine further`

### Information Gaps
- Uncertain facts → Search immediately
- Uncertain requirements → Ask user immediately
- **Never** assume and continue

---

## Execution Flow (Detailed Steps)

### Phase 1: Initialize (Must Execute)

1. **Assess problem complexity**
   - Read user problem
   - Determine rounds: simple 2-3, medium 4-5, complex 5-7, wicked 7-10

2. **Create working directory**
   ```bash
   mkdir -p reinforced-thinking
   ```

3. **Write problem definition file**
   Create `reinforced-thinking/problem.md`, containing:
   - Problem background
   - Current system/environment state
   - Core problem
   - Constraints
   - Success criteria
   - Complexity assessment rationale

---

### Phase 2: Iterate (Must Execute for Each Round)

For round X, execute these steps in order:

#### Step 2.1: Read Files
```bash
# Read problem definition
read reinforced-thinking/problem.md

# Read previous round (skip for round 1)
read reinforced-thinking/round_{X-1}.md
```

#### Step 2.2: Reset Mindset
Before writing, explicitly tell yourself:
- "I will think about this problem from a **fresh angle**"
- "I cannot copy the previous round's approach"
- "If this is the **last round**, I must provide a complete solution"

#### Step 2.3: Choose Angle Freely
- Critically review the previous round's solution
- If needed, choose an angle **significantly different** from the previous round
- If needed, **completely overturn** the previous round

#### Step 2.4: Think All-Out and Write
Create `reinforced-thinking/round_X.md`, **must include this structure**:

```markdown
# Round X

## Independence Declaration
This is round X. If this were the last round, I would be completely satisfied with this solution.

---

## Core Insight
(What essential problem did you discover? 1-2 sentences)

## Solution Design
(Describe the complete solution in detail, including steps, code examples, configs, etc.)

## Expected Results
(Effects after implementing the solution)

## Risks and Mitigations
(Potential risks + countermeasures)

## Why This Solution is Complete?
(Explain why this solution can be implemented directly without "future improvements")
```

#### Step 2.5: Self-Review (Quality Check)
**Before saving, must check:**

- [ ] **Final Quality Test**: If this were the last round, would I be satisfied?
- [ ] **Zero TODO Check**: Any `TODO`, `to be improved`, `next round` in the text?
- [ ] **Information Completeness Check**: Are all needed details written?
- [ ] **Executability Check**: Can the solution be implemented directly?
- [ ] **Independent Thinking Check**: Is it based on problem.md + only previous round?

**If any check fails → Redo Step 2.4**

#### Step 2.6: Save File
```bash
write reinforced-thinking/round_X.md
```

---

### Phase 3: Synthesize (Must Execute)

1. **Read all rounds**
   ```bash
   read reinforced-thinking/problem.md
   read reinforced-thinking/round_1.md
   read reinforced-thinking/round_2.md
   # ... read all rounds
   ```

2. **Analyze all solutions**
   - Identify unique value of each solution
   - Identify conflicts and complements between solutions
   - Select best solution or combined solution

3. **Generate final report**
   Create `reinforced-thinking/final_report.md`:

   ```markdown
   # Final Report

   ## Problem Restatement
   (One sentence summarizing the problem)

   ## Round Summaries
   - R1: Angle - Core Solution - Advantage
   - R2: Angle - Core Solution - Advantage
   - ...

   ## Solution Comparison
   | Solution | Advantages | Disadvantages | Applicable Scenarios |

   ## Recommended Solution
   (Select best or combined solution with reasoning)

   ## Implementation Plan
   (Specific implementation steps)

   ## Risks and Notes
   ```

---

### Phase 4: Cleanup (Must Execute)

**After generating the final report, you MUST ask the user whether to clean up intermediate files.**

1. **List generated files**
   ```bash
   ls -la reinforced-thinking/
   ```

2. **Ask user explicitly**
   
   Present this to the user:
   ```
   强化思考完成！生成了以下文件：
   
   📄 final_report.md    (最终报告 - 保留)
   📄 problem.md          (问题定义)
   📄 round_1.md          (第1轮方案)
   📄 round_2.md          (第2轮方案)
   ...
   
   是否清理中间文件（round_*.md, review_*.md, problem.md）？
   只保留 final_report.md
   ```

3. **Wait for user confirmation**
   
   - If user says **YES/是/清理**: Delete intermediate files
     ```bash
     rm reinforced-thinking/problem.md
     rm reinforced-thinking/round_*.md
     rm reinforced-thinking/review_*.md
     ```
   - If user says **NO/否/保留**: Keep all files

4. **Never auto-cleanup without asking** - Always wait for user decision

---

## Quality Assurance Mechanism

### Mandatory Redo Rules

If ANY of these conditions trigger, **MUST redo current round**:

1. **Contains forbidden words**: `TODO`, `to be improved`, `next round`, `later`, `refine further`
2. **Not final quality**: Not satisfied, needs "future supplements"
3. **Depends on unauthorized files**: Read files other than problem.md and round_{X-1}.md
4. **Incomplete solution**: Missing core parts (problem analysis, solution, expected results, risks)

### Checklist (Must Do Each Round)

After completing each round, verify:

```
□ I chose a different angle from the previous round
□ I did not copy the previous round's solution
□ No TODO, "to be improved" in the solution
□ If this were the last round, I would be satisfied
□ All needed details are included
□ Solution can be implemented directly, no "future development" needed
□ Only read problem.md and previous round
```

---

## Common Errors and Fixes

| Error | Example | Fix |
|-------|---------|-----|
| Carry context | "Based on R1's UX and R2's tech..." | Only write "Based on problem.md and R3's approach..." |
| Leave TODOs | "Details next round" | Give core design details now |
| Assume facts | "Users probably want X" | Search to confirm or ask user |
| Preset direction | "Next round: security angle" | Let each round choose freely |
| Iterative thinking | "Improve on R1" | Each round is independent, think from scratch |
| No details | "See related docs" | Write complete details directly in file |

---

## Best Practices

- **Divergent thinking**: No angle matrix—choose any perspective freely
- **True independence**: Only read problem.md + previous round, not all history
- **All-out each round**: Don't hold back for "next iteration"
- **Transparency**: Show chosen angle and reasoning in each round
- **Convergence**: If 2 consecutive rounds lack true innovation, suggest ending early
