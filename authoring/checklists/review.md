# Skill Review Checklist

- [ ] Folder name is lowercase hyphen-case and matches `SKILL.md` frontmatter `name`.
- [ ] `SKILL.md` frontmatter contains only `name` and `description`.
- [ ] `description` includes clear trigger conditions.
- [ ] `description` is not so broad that it steals unrelated requests.
- [ ] Long documentation is in `references/`, not the main body.
- [ ] Every reference file is directly linked or named from `SKILL.md`.
- [ ] Scripts are executable or have clear invocation commands.
- [ ] Scripts avoid leaking credentials through command-line arguments.
- [ ] Destructive or production operations require user confirmation.
- [ ] `agents/openai.yaml` is present when UI metadata matters.
- [ ] `registry/skills.yaml` includes the skill.
- [ ] `python3 scripts/validate-skills` passes.
