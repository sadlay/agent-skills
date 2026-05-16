# Create Skill Prompt

Use this prompt when asking an AI agent to create a new skill for this repository.

```text
You are creating a new Agent Skill for the repository at <repo-path>.

Goal:
- Convert the user's concrete workflow into a reusable skill under `skills/<skill-name>/`.
- Keep the skill concise, portable, and compatible with Claude and Codex where possible.

Inputs:
- User request: <paste request>
- Example prompts that should trigger the skill: <paste examples>
- Example prompts that should not trigger the skill: <paste examples>
- Required tools, APIs, credentials, or files: <paste constraints>

Instructions:
1. Choose a lowercase hyphen-case skill name under 64 characters.
2. Create `skills/<skill-name>/SKILL.md` with only `name` and `description` in YAML frontmatter.
3. Make `description` specific enough to trigger correctly. Include both use cases and exclusions when important.
4. Keep core workflow instructions in `SKILL.md`.
5. Add `references/` only for detailed documentation the agent should load on demand.
6. Add `scripts/` only for deterministic or repeatedly rewritten operations.
7. Add `assets/` only for files used as output resources or templates.
8. Add `agents/openai.yaml` for UI metadata when the skill should appear cleanly in Codex/OpenAI skill lists.
9. Add or update `registry/skills.yaml`.
10. Run `python3 scripts/validate-skills`.

Output:
- Summarize created files.
- List any assumptions.
- List validation results.
```
