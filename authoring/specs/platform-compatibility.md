# Platform Compatibility

## Source of Truth

`skills/` is the source of truth. Plugin package directories under `plugins/` are generated copies.

## Claude

Claude and Claude Code use skill folders with `SKILL.md`. Claude Code plugin distribution expects plugin skills to live inside the plugin package.

Use `.claude-plugin/marketplace.json` at the repository root to expose installable plugins.

## Codex

Codex plugin packages require `.codex-plugin/plugin.json`. The plugin can point to a local `skills/` directory inside the plugin package.

Use `.agents/plugins/marketplace.json` at the repository root to expose local Codex plugins.

## Writing Portable Skills

Prefer platform-neutral wording:

- Say "use the available shell command" instead of naming a platform-specific tool.
- Say "ask the user for confirmation" instead of naming one UI-specific question tool.
- Include platform-specific instructions only when the workflow depends on that platform.

When a skill must be platform-specific, say so in the frontmatter `description` and registry entry.
