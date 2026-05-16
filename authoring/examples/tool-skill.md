# Tool Skill Example

```markdown
---
name: example-cli-tool
description: Use when the user asks Codex to operate Example CLI projects, inspect Example CLI configuration, run Example CLI diagnostics, or modify Example CLI workflows. Do not use for general shell scripting or unrelated command-line tools.
---

# Example CLI Tool

Use the installed `example` command to inspect and operate Example CLI projects.

## Workflow

1. Check whether the current directory is an Example project.
2. Run `example status` before making changes.
3. Prefer read-only commands unless the user explicitly asks for changes.
4. For destructive operations, explain the affected files and ask for confirmation.

## References

For command details, read `references/commands.md` only when needed.
```
