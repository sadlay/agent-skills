---
name: skill-author
description: Create, review, or improve Agent Skills in this repository. Use when the user asks to write a new skill, update an existing skill, design skill triggers, split skill references, generate skill UI metadata, validate skills, or package skills for Claude/Codex distribution.
---

# Skill Author

Use this skill to turn repeated workflows into portable Agent Skills for this repository.

## Workflow

1. Clarify the recurring workflow, target users, platform constraints, and concrete trigger examples.
2. Choose a lowercase hyphen-case name under 64 characters.
3. Create or update `skills/<skill-name>/SKILL.md`.
4. Keep `SKILL.md` focused on trigger behavior and core procedure.
5. Move detailed documentation into directly linked files under `references/`.
6. Put deterministic helper code in `scripts/` and reusable output resources in `assets/`.
7. Add `agents/openai.yaml` when the skill should appear well in Codex/OpenAI skill lists.
8. Update `registry/skills.yaml`.
9. Run `python3 scripts/validate-skills`.
10. Run `python3 scripts/sync-plugin-skills` when the skill should be packaged.

## Authoring Prompts

Use the repository prompt files when they fit the task:

- `references/create-skill-prompt.md` for new skills
- `references/review-skill-prompt.md` for reviews
- `references/improve-skill-prompt.md` for iteration after real use
- `references/generate-openai-yaml-prompt.md` for UI metadata

## Rules

- Do not put unfinished skills in `skills/`; use `drafts/`.
- Do not copy upstream specification repositories into the root.
- Do not add broad trigger descriptions that capture unrelated requests.
- Do not add scripts that require credentials without documenting safe usage and confirmation points.

Read `references/authoring-workflow.md` for repository-specific standards when making substantial changes.
