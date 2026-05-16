# Authoring Workflow

## Source Layout

Create production skills in `skills/<skill-name>/`. Use `drafts/` for experiments.

Use this shape:

```text
skills/<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── assets/
```

Only create optional directories when they are useful.

## Trigger Design

The frontmatter `description` is the primary trigger surface. Include:

- What the skill does.
- Which user requests should trigger it.
- Which nearby requests should not trigger it when confusion is likely.
- Platform-specific constraints if any.

## Progressive Disclosure

Keep `SKILL.md` short enough to load without wasting context. Move details into `references/` when they are:

- Long command references.
- API documentation.
- Business rules.
- Large examples.
- Platform-specific variants.

Link every reference file from `SKILL.md` or make its purpose obvious in a directly linked reference.

## Packaging

Run `python3 scripts/sync-plugin-skills` after changing active skills. Generated plugin directories should not be hand-edited except their manifest metadata.

## Validation

Run `python3 scripts/validate-skills`. Fix frontmatter, naming, registry, and generated-package errors before publishing.
