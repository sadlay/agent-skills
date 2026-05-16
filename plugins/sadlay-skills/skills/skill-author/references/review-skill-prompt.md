# Review Skill Prompt

Use this prompt to review an existing skill before publishing or installing it.

```text
Review the skill at `<skill-path>` for this multi-platform Agent Skills repository.

Focus on:
1. Triggering: Is the `description` precise, complete, and not too broad?
2. Portability: Does the skill avoid platform-specific tool names unless required?
3. Context hygiene: Should long sections move from `SKILL.md` into `references/`?
4. Safety: Do destructive, external, credentialed, or production operations require confirmation?
5. Resources: Are `scripts/`, `references/`, and `assets/` used only when they help?
6. Validation: Does the folder name match frontmatter `name`?
7. UI metadata: Does `agents/openai.yaml` match the skill's actual behavior?

Return:
- Findings ordered by severity.
- Exact file and line references when possible.
- Suggested patches only for issues that are clear and low risk.
```
