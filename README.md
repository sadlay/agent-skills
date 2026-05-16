# Agent Skills

[中文](README.zh-CN.md) | English

This repository is a personal, multi-platform skill collection. It keeps the source of truth in `skills/`, then packages those skills for Claude Code and Codex plugin distribution.

## Install

### Claude Code

Add this repository as a plugin marketplace:

```text
/plugin marketplace add sadlay/agent-skills
```

Then install the plugin:

```text
/plugin install sadlay-skills@sadlay-skills-marketplace
```

For local development, add the checked-out repository instead:

```text
/plugin marketplace add /Users/sadlay/WorkSpace/github/agent-skills
/plugin install sadlay-skills@sadlay-skills-marketplace
```

### Codex

Codex does not need the `python3` commands below for normal use. Add the local plugin package or local marketplace path in the Codex app/plugin UI:

```text
plugins/codex-sadlay-skills
```

Or:

```text
.agents/plugins/marketplace.json
```

The `python3` commands are only for repository maintainers. Run them after changing files under `skills/` so generated plugin packages stay in sync:

```bash
python3 scripts/sync-plugin-skills
python3 scripts/validate-skills
```

### Manual Copy

If a platform only supports direct skill folders, copy individual directories from `skills/` into that platform's skill directory.

## Repository Layout

- `skills/` - production-ready skills. Each child directory is a standalone skill with `SKILL.md`.
- `drafts/` - unfinished skill ideas that should not be installed or packaged.
- `authoring/` - prompts, specs, checklists, and examples for creating skills with AI assistance.
- `plugins/sadlay-skills/` - Claude Code plugin package generated from `skills/`.
- `plugins/codex-sadlay-skills/` - Codex plugin package generated from `skills/`.
- `.claude-plugin/marketplace.json` - Claude Code marketplace descriptor for this repository.
- `.agents/plugins/marketplace.json` - Codex marketplace descriptor for this repository.
- `registry/skills.yaml` - human-maintained index of skills, status, category, and platform support.
- `scripts/` - validation, sync, install, and packaging helpers.
- `third_party/` - optional upstream references such as `agentskills/agentskills`.

## Workflow

1. Draft or update a skill in `skills/<skill-name>/`.
2. Run `python3 scripts/validate-skills`.
3. Run `python3 scripts/sync-plugin-skills`.
4. Test the generated plugin directories.
5. Commit source and generated plugin manifests together.

## Skill Shape

Minimum:

```text
skills/<skill-name>/
└── SKILL.md
```

Full:

```text
skills/<skill-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
├── scripts/
└── assets/
```

`SKILL.md` should stay concise. Put large documentation in `references/`, deterministic helpers in `scripts/`, and output resources in `assets/`.

## Upstream References

This project follows the Agent Skills directory model. The upstream specification and reference SDK live at:

- https://agentskills.io/specification
- https://github.com/agentskills/agentskills

Do not vendor upstream files into the root of this project. If needed, add them under `third_party/agentskills`.
