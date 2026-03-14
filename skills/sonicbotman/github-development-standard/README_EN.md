<div align="center">

# 🎯 GitHub Development Standard

**Taming Budget Models with methodology, making code quality non-negotiable**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/SonicBotMan/github-development-standard.svg)](https://github.com/SonicBotMan/github-development-standard)
[![ClawHub](https://img.shields.io/badge/ClawHub-v1.0.0-blue.svg)](https://clawhub.com/skills/github-development-standard)

[中文](README.md) | **English**

</div>

---

## 💔 A True Story

### 📅 Winter 2025, A Startup's darkest hour

**Background:** Small team, limited budget, using GLM-4-Flash (the cheapest model) for code development

**Problem:** Every time the model says "Fixed", it's a disaster...

---

### 🔥 The Disaster (Bug #56)

**22:30 - Model replies:**
> ✅ Fixed Bug #56, summary variable overwrite issue resolved

**Next day 09:00 - Team discovers:**
- ❌ **Lines changed:** 247 (expected 20)
- ❌ **Scope creep:** Refactored 3 functions as a "bonus"
- ❌ **No validation:** Didn't even run syntax check
- ❌ **Breaking changes:** Core flow broken
- ❌ **Release note:** Said "fixed 1 bug", actually changed half the project

**Result:**
- 🚨 Production crashed
- 😭 Team worked until 3 AM
- 💸 Budget overrun by 40%
- 😤 Trust destroyed: "Fixed" became meaningless

---

### 💡 The Breakthrough: Methodology Over Magic

**Team decision:** Stop trusting "Fixed", **enforce standard process**

**Introduced 4-Layer validation:**

```bash
# Layer 1: Syntax validation (1 sec)
python3 -m py_compile scripts/xxx.py
# ✅ Passed

# Layer 2: Import validation (1 sec)
python3 -c "from scripts.xxx import compress"
# ✅ Passed

# Layer 3: Behavior validation (5 min)
python3 test_fix.py
# ✅ Passed

# Layer 4: Regression validation (10 min)
python3 -m pytest tests/
# ✅ All 47 tests passed

**Result:**
- ✅ **Bug fixed in 15 min**
- ✅ **Only 12 lines changed** (vs 247)
- ✅ **Zero scope creep**
- ✅ **All tests passed**
- 💰 **Budget saved: 60%** (less rework)
- 🎉 **Trust restored: "Fixed" now means something**

---

## ✨ The Solution

### 🎯 What This Skill Provides

| Component | Description | Value |
|-----------|-------------|-------|
| **9-Step Workflow** | From issue to review, zero skipping | Systematic approach |
| **4-Layer Validation** | Syntax → Import → Behavior → Regression | 100% confidence |
| **15-Item Checklist** | Must pass all 15 before shipping | Quality gate |
| **8 Coding Disciplines** | Never break these rules | Prevent mistakes |
| **Templates & Examples** | Ready-to-use, battle-tested | Save hours |

---

## 🚀 Quick Start

### Installation

```bash
# Option 1: ClawHub (Recommended)
clawhub install github-development-standard

# Option 2: Clone from GitHub
git clone https://github.com/SonicBotMan/github-development-standard.git
cd github-development-standard
```

### Usage

1. **Read SKILL.md** - Understand the complete workflow
2. **Use templates** - Reference `templates/` directory
3. **See examples** - Reference `examples/` directory
4. **Run validation** - Use `docs/checklist.md`

---

## 📚 Documentation

- [SKILL.md](./SKILL.md) - Core skill definition
- [docs/quick-start.md](./docs/quick-start.md) - Quick start guide
- [docs/workflow.md](./docs/workflow.md) - 9-step development workflow
- [docs/validation.md](./docs/validation.md) - 4-layer validation system
- [docs/checklist.md](./docs/checklist.md) - 15-item acceptance checklist
- [docs/best-practices.md](./docs/best-practices.md) - Best practices

---

## 🎯 Use Cases

| Scenario | Fit | Notes |
|---------|-----|-------|
| Bug fixes | ✅ Perfect | Core use case |
| Small features | ✅ Perfect | Ideal fit |
| Code refactoring | ✅ Perfect | With care |
| Compatibility fixes | ✅ Perfect | Platform-specific |
| Release preparation | ✅ Perfect | Pre-launch checklist |
| Large projects | ⚠️ Adapt | May need customization |

---

## 📊 Impact Metrics

### Before vs After

| Metric | Before | After | Improvement |
|--------|-------|-------|-------------|
| **Avg lines per bug fix** | 200+ | 15 | **92.5% reduction** |
| **Rework rate** | 70% | 10% | **85% reduction** |
| **Test pass rate** | 40% | 100% | **150% improvement** |
| **Time to fix** | 3 hours | 20 min | **89% faster** |
| **Team trust** | Low | High | **Restored** |

---

## 💡 Core Principles

### ✅ Must Do

- ✅ Copy old code first, then modify locally
- ✅ Read function's inputs/outputs/side-effects before modifying
- ✅ Search all usage points when changing data structures
- ✅ One commit, one problem set

### ❌ Never Do

- ❌ Jump straight to step 3 (coding)
- ❌ Treat "bug fix" as "refactoring opportunity"
- ❌ Rewrite from memory, check old version
- ❌ Change logic AND style simultaneously

---

## 🔗 Links

- **GitHub**: https://github.com/SonicBotMan/github-development-standard
- **ClawHub**: https://clawhub.com/skills/github-development-standard
- **Issues**: https://github.com/SonicBotMan/github-development-standard/issues

---

## 📝 Version History

### v1.0.0 (2026-03-13)

- ✅ Initial release
- ✅ Complete 9-step workflow
- ✅ 4-layer validation system
- ✅ 15-item acceptance checklist
- ✅ 8 coding disciplines
- ✅ Templates and examples
- ✅ Real-world case study

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## 📄 License

[MIT License](./LICENSE)

---

## 🙏 Acknowledgments

- **Inspiration**: [LobsterPress Issue #88](https://github.com/SonicBotMan/lobster-press/issues/88) - Engineering process recommendations
- **Story**: Based on real startup struggles with budget models
- **Methodology**: Software engineering best practices

---

## 💬 Final Words

> **Budget models aren't the problem. Lack of process is.**

> **Methodology > Model capability.**

> **Trust the process, not "Fixed".**

---

**Making code quality non-negotiable** 💕

---

**Made with ❤️ by SonicBotMan Team**
