# Skill Writing Guide

## Purpose

Skills are operational memory for agents. They should teach an agent how to perform a recurring workflow that is too specific, fragile, or context-heavy to rediscover every time.

## Structure

Every production skill lives in `skills/<skill-name>/` and must include `SKILL.md`.

Use optional resource directories only when they serve a clear role:

- `references/` for detailed documentation loaded on demand.
- `scripts/` for deterministic helpers or repeated code.
- `assets/` for templates, images, fonts, examples, or other output resources.
- `agents/openai.yaml` for UI metadata.

## Frontmatter

Use only:

```yaml
---
name: skill-name
description: Clear trigger description with when-to-use details.
---
```

The `description` is the main trigger surface. Put trigger conditions there, not deep in the body.

## Body

Write instructions as imperative workflow guidance. Prefer concise rules, concrete commands, and clear decision points.

Avoid:

- Long background essays.
- Generic advice the base model already knows.
- Tool names that only exist in one platform unless the skill is platform-specific.
- Unlinked reference files.
- Unvalidated scripts.

## Good Skill Boundaries

A good skill has one center of gravity:

- A tool workflow, such as operating a CLI.
- A domain workflow, such as preparing a release note.
- A file workflow, such as editing a specific document format.
- A company workflow, such as querying an internal system safely.

Split a skill when it contains unrelated triggers, unrelated tools, or conflicting safety rules.
