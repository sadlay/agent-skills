# Agent Skills Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first repository scaffold for a personal, multi-platform Agent Skills collection.

**Architecture:** Keep `skills/` as the source of truth, use `authoring/` for AI-facing creation prompts and quality rules, and generate platform plugin packages under `plugins/`. Validation is intentionally lightweight and local so new skills can be added without depending on network access.

**Tech Stack:** Markdown, JSON, YAML-like registry files, and Python 3 standard library scripts.

---

### Task 1: Create Repository Skeleton

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `NOTICE`
- Create: `package.json`
- Create: `pyproject.toml`
- Create: `registry/skills.yaml`

- [x] Add the root documentation and project metadata.
- [x] Define `skills/` as the source of truth and plugin directories as generated packages.

### Task 2: Add Authoring System

**Files:**
- Create: `authoring/prompts/create-skill.md`
- Create: `authoring/prompts/review-skill.md`
- Create: `authoring/prompts/improve-skill.md`
- Create: `authoring/prompts/generate-openai-yaml.md`
- Create: `authoring/specs/skill-writing-guide.md`
- Create: `authoring/specs/platform-compatibility.md`
- Create: `authoring/checklists/review.md`
- Create: `authoring/checklists/release.md`
- Create: `authoring/examples/tool-skill.md`

- [x] Add prompt files for AI-assisted skill creation and review.
- [x] Add repository-specific writing standards and release checks.

### Task 3: Add Distribution Manifests

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `plugins/sadlay-skills/.claude-plugin/plugin.json`
- Create: `plugins/codex-sadlay-skills/.codex-plugin/plugin.json`

- [x] Add marketplace descriptors for Claude and Codex.
- [x] Use non-reserved marketplace and plugin names.

### Task 4: Add Skill Author Skill

**Files:**
- Create: `skills/skill-author/SKILL.md`
- Create: `skills/skill-author/agents/openai.yaml`
- Create: `skills/skill-author/references/authoring-workflow.md`
- Create: `skills/skill-author/assets/templates/SKILL.md`

- [x] Package the authoring rules as an installable skill.

### Task 5: Add Scripts and Verify

**Files:**
- Create: `scripts/validate-skills`
- Create: `scripts/sync-plugin-skills`
- Create: `scripts/install-claude`
- Create: `scripts/install-codex`

- [x] Add standard-library Python scripts.
- [x] Run validation.
- [x] Sync plugin skills.
- [x] Initialize git if needed.
