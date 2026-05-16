---
name: codex-provider-sync
description: Restore Codex historical session visibility after switching model_provider or provider/account. Use when Codex Desktop, Codex CLI /resume, or project recent sessions stop showing old conversations after a provider switch; when the user asks to resync Codex history, recover missing sessions, inspect provider/session metadata, install or run codex-provider-sync, switch provider and sync metadata, or restore a provider-sync backup.
---

# Codex Provider Sync

## Overview

Use the installed `codex-provider` CLI from `codex-provider-sync` to repair Codex session visibility metadata. The tool updates rollout metadata, SQLite thread metadata, and project workspace cache data; do not manually edit only one of those stores unless the tool is unavailable and the user explicitly asks for manual repair.

Read `references/behavior.md` when you need command semantics, output interpretation, risk boundaries, or troubleshooting details.

## Default Workflow

1. Confirm the target Codex home. Default to `${CODEX_HOME}` when set, otherwise `~/.codex`. Pass `--codex-home PATH` only when the user gives a non-default home.
2. Ensure the `codex-provider` CLI is available:
   - Run `command -v codex-provider` on macOS/Linux or `where codex-provider` on Windows.
   - If missing, follow `references/behavior.md#new-environment-installation` before continuing.
   - After installing or locating the CLI, run `codex-provider status` to verify it starts.
3. Run `codex-provider status` first unless the user explicitly gave a backup restore path or a specific command to run.
4. Read `Current provider`, rollout provider counts, SQLite provider counts, project visibility diagnostics, locked rollout file count, encrypted content warnings, and backup root.
5. Choose the narrowest command:
   - Use `codex-provider sync` when the user already switched provider/auth elsewhere and wants old sessions visible under the current provider.
   - Use `codex-provider sync --provider <id>` when the target provider is clear but `config.toml` should not be changed.
   - Use `codex-provider switch <id>` when the user wants the root `model_provider` changed and session metadata synced in one operation.
   - Use `codex-provider restore <backup-dir>` when the user wants to roll back a previous sync or synced to the wrong provider.
   - Use `codex-provider prune-backups --keep <n>` only for managed backup cleanup.
6. Report the final provider, whether rollout files and SQLite are aligned, backup location for sync/switch operations, and any partial success caused by locked rollout files.

## Commands

```bash
codex-provider status
codex-provider sync
codex-provider sync --provider openai
codex-provider switch apigather
codex-provider restore ~/.codex/backups_state/provider-sync/<timestamp>
codex-provider prune-backups --keep 5
```

With an explicit Codex home:

```bash
codex-provider status --codex-home /path/to/.codex
codex-provider sync --codex-home /path/to/.codex
codex-provider switch openai --codex-home /path/to/.codex
```

When the CLI is missing and Node.js 24+ is available:

```bash
npm install -g git+https://github.com/Dailin521/codex-provider-sync.git
codex-provider status
```

## Safety Rules

- Treat `status` as read-only.
- Expect `sync` and `switch` to create backups under `~/.codex/backups_state/provider-sync/<timestamp>`.
- Do not edit `auth.json`, login state, message content, titles, or `updated_at`.
- Do not force old sessions into Codex Desktop's recent 50 by changing timestamps.
- Warn that histories containing `encrypted_content` from another provider/account may become visible but can still fail on continue or compact with `invalid_encrypted_content`.
- If the CLI is missing, first check whether the user installed it globally or locally. Prefer using the installed `codex-provider` command; otherwise install it with user approval or run it from a located local project.

## Error Handling

- If `state_5.sqlite is currently in use`, tell the user to close Codex, Codex Desktop/App, and app-server, then rerun the same command.
- If output reports skipped locked rollout files, treat the operation as partial success. List the skipped paths shown in output and tell the user to rerun `codex-provider sync` after the active session ends.
- If `switch <provider-id>` says the provider is unavailable, tell the user to define it in `config.toml` or switch auth/provider with their existing provider tool first, then run `codex-provider sync`.
- If `state_5.sqlite` is malformed or unreadable, stop. Tell the user the tool refused to sync and that the database must be backed up, repaired, or restored before retrying.
