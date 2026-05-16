# Generate OpenAI YAML Prompt

Use this prompt to create or refresh `agents/openai.yaml` for a skill.

```text
Generate `agents/openai.yaml` for the skill at `<skill-path>`.

Read `SKILL.md`, then produce concise UI metadata:
- `display_name`: human-readable name, title case.
- `short_description`: one sentence under 120 characters.
- `default_prompt`: one realistic prompt that would trigger this skill.

Rules:
1. Do not invent capabilities not present in `SKILL.md`.
2. Keep text user-facing and concrete.
3. Do not include optional branding fields unless already provided by the user.
4. Preserve existing custom fields if updating an existing file.
```
