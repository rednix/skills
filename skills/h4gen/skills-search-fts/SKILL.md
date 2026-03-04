---
name: skills-search-fts
description: Search a specialized database of 240,000+ Agent skills using FTS5 boolean logic.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
    files: ["scripts/*"]
    emoji: "🔍"
---

# Agent Skills Search

Use this skill to discover specialized tool definitions, system prompts, and agent configurations from a massive index of 240,000+ skills.

## Usage

Search for skills by keywords or boolean operators (AND, OR, NOT) using the included search helper.

```bash
python3 scripts/search.py "YOUR_QUERY"
```

## Example Queries

- **Basic**: `python3 scripts/search.py "python"`
- **Advanced (Boolean)**: `python3 scripts/search.py "python AND machine learning"`
- **Strict Matching**: `python3 scripts/search.py "'web scraper'"`

## Response Format

The search tool returns the top 50 matching skills with metadata (name, description, tags, source) formatted for easy reading.
