---
name: im-framework
description: |
  Reference, explain, and apply the Immanent Metaphysics (IM) framework by Forrest Landry.
  Uses a structured ontology of 767 entities (concepts, axioms, theorems, terms, aphorisms, implications)
  with direct links to the source text at mflb.com. Use when asked to explain IM concepts, apply the
  framework to a situation, trace derivation chains, find source references, or connect ideas across
  the whitebook. Triggers on: "immanent metaphysics", "IM framework", modality questions, axiom
  references, ICT, symmetry/continuity ethics, effective choice, path of right action, or any
  request to ground claims in the framework.
---

# Immanent Metaphysics Framework

Assess what someone is doing with the tools of the IM and provide grounded, sourced responses with direct links to Forrest Landry's whitebook at mflb.com.

## Bundled Reference Files

All in `references/` (relative to this skill):

| File | Contents |
|------|----------|
| `graph.jsonl` | 767 entities: 134 Concepts, 3 Axioms, 11 Theorems, 147 Aphorisms, 4 Implications. Each has `name`, `definition`, `source_section`, `location` (URL). Relations: implies, paired_with, contrasts_with, depends_on, has_modality, illuminates, defined_in. |
| `whitebook-map.jsonl` | 73 entries mapping whitebook structure (chapters, sections, URLs). Entry point: https://mflb.com/8192 |
| `schema.yaml` | Type definitions and relation types for the ontology. |

Full source texts (not bundled, available at mflb.com):
- An Immanent Metaphysics (full book): https://mflb.com/8192
- Aphorisms of Effective Choice: https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch5.htm

## How to Use

### 1. Search the Ontology

```bash
# Find a concept by name
grep -i '"name": "symmetry"' references/graph.jsonl

# Find all entities mentioning a term
grep -i 'continuity' references/graph.jsonl | head -10

# Find entities with source URLs
python3 -c "
import json
for line in open('references/graph.jsonl'):
    d = json.loads(line)
    if 'entity' in d:
        props = d['entity'].get('properties',{})
        loc = props.get('location','')
        name = props.get('name', props.get('word', props.get('text','')))
        if 'SEARCH_TERM' in name.lower() or 'SEARCH_TERM' in props.get('definition','').lower():
            print(f'{d[\"entity\"][\"type\"]}: {name}')
            if loc: print(f'  URL: {loc}')
            print(f'  Def: {props.get(\"definition\",\"\")[:200]}')
            print()
"

# Find relations for a specific entity
grep '"ENTITY_ID"' references/graph.jsonl | grep relation
```

### 2. Link to Source

Every entity with a `location` property has a direct URL to the relevant whitebook section at mflb.com. Always include these links when citing.

Key chapter URLs:

| Topic | URL |
|-------|-----|
| Modalities | [Ch1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1_modalities) |
| Axioms | [Ch1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1_axioms) |
| ICT | [Ch3](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch3.htm#1_ict) |
| Symmetry / Continuity | [Ch3](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch3.htm#1_symmetry) |
| Ethics | [Ch6](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm) |
| Path of Right Action | [Ch6](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm#2_path) |
| Basal Motivations | [Ch6](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm#2_basal) |
| Aesthetics | [Ch7](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch7.htm) |
| Mind | [Ch8](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch8.htm) |
| Evolution | [Ch9](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch9.htm) |

### 3. Assess and Apply

1. **Identify which modality, axiom, or theorem they're engaging with.** Search the ontology.
2. **Check for modal confusion.** Collapsing omniscient into immanent? Treating transcendent as omniscient? Axiom III (distinct, inseparable, non-interchangeable) is the diagnostic.
3. **Trace derivation chains.** Use `implies`, `depends_on`, `has_modality` relations.
4. **Link to source.** Always provide the mflb.com URL.
5. **Connect to aphorisms.** The 147 aphorisms illuminate practical application.

## Quick Reference

### The Three Modalities

**Immanent** — relational, interactive, participatory. First-person experience. The center of any continuum.

**Omniscient** — structural, external, fixed. Third-person observation. The whole seen at once.

**Transcendent** — possibility, precondition, a priori. No fixed position. True at all locations.

### The Three Axioms

**I:** The immanent is more fundamental than the omniscient and/or the transcendent. The omniscient and transcendent are conjugate.

**II:** A class of the transcendent precedes an instance of the immanent. A class of the immanent precedes an instance of the omniscient. A class of the omniscient precedes an instance of the transcendent.

**III:** The immanent, omniscient, and transcendent are distinct, inseparable, and non-interchangeable.

### The ICT (Incommensuration Theorem)

From six intrinsics of comparison (sameness, difference, content, context, subject, object):

- **Continuity** = sameness of content where sameness of context
- **Symmetry** = sameness of content where difference of context
- **Asymmetry** = difference of content where difference of context
- **Discontinuity** = difference of content where sameness of context

**Result:** Symmetry + Continuity cannot both apply absolutely. Valid conjunctions: (Continuity + Asymmetry) OR (Symmetry + Discontinuity).

**Cross-domain:** Bell's Theorem (physics), Godel's Incompleteness (logic), Causality without Determinism (metaphysics).

### Ethics

**Symmetry Ethics:** When inner being is unchanged, expression should be the same regardless of external circumstances.

**Continuity Ethics:** When inner nature is unchanged, the way of relating should remain the same regardless of what or whom one relates to.

These derive from the valid conjunctions of the ICT applied to action. They cannot both be perfectly realized simultaneously.

### Path of Right Action

It is always possible to choose win-win for all involved, at all levels of being. Win-win choices are mutually self-supporting and form a contiguous path. The degree to which win-win seems impossible is the measure of deviation from the path.

## Entity Types in the Ontology

| Type | Count | Contains |
|------|-------|----------|
| Concept | 134 | Named ideas with definitions, modality assignments, source URLs |
| Axiom | 3 | Foundational axioms with statements and implications |
| Theorem | 11 | ICT, Symmetry Ethics, Continuity Ethics, Identity, Bell's mapping, Godel mapping |
| Aphorism | 147 | From Effective Choice, with themes and illumination links |
| Implication | 4 | Cross-domain applications (physics, logic, ethics, consciousness) |

## Attribution

Always attribute to Forrest Landry's Immanent Metaphysics. Distinguish:
1. **Direct citation** — quote with source URL
2. **Close paraphrase** — summary with source URL
3. **Agent synthesis** — your own application, labeled as such

Do not invent positions or imply endorsement of claims not grounded in source material.
