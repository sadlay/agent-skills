# codex-provider-sync Behavior Reference

## Purpose

`codex-provider-sync` makes historical Codex sessions visible again after `model_provider` changes. The common failure mode is metadata mismatch, not lost session files.

The tool synchronizes:

- `~/.codex/sessions`
- `~/.codex/archived_sessions`
- `~/.codex/state_5.sqlite`
- `~/.codex/.codex-global-state.json` and its backup file

## Command Semantics

- `status`: Inspect current root provider, configured providers, rollout provider distribution, SQLite provider distribution, encrypted content counts, project visibility, and managed backups.
- `sync`: Keep the root `model_provider` unchanged and synchronize historical metadata to the current provider from `config.toml`; if missing, it uses implicit default `openai`.
- `sync --provider <id>`: Synchronize historical metadata to the provider id without changing `config.toml`.
- `switch <id>`: Validate the provider id exists in `config.toml`, rewrite the root `model_provider`, then run sync.
- `restore <backup-dir>`: Restore from a managed provider-sync backup. Supports `--no-config`, `--no-db`, and `--no-sessions`.
- `prune-backups --keep <n>`: Delete only managed backups under `backups_state/provider-sync`, keeping the newest `n`.

CLI requires Node.js 24+ because it uses `node:sqlite`.

## New Environment Installation

Skills do not auto-run installers when loaded. When `codex-provider` is missing, guide Codex to install or locate the CLI before running sync commands.

Detection:

```bash
command -v codex-provider
node -v
npm -v
```

On Windows, use:

```powershell
where codex-provider
node -v
npm -v
```

If `codex-provider` is missing and Node.js is 24 or newer, install from the GitHub repo:

```bash
npm install -g git+https://github.com/Dailin521/codex-provider-sync.git
codex-provider status
```

If global install is not acceptable or fails because of permissions, locate a local clone and run from it:

```bash
git clone https://github.com/Dailin521/codex-provider-sync.git
cd codex-provider-sync
npm install
node src/cli.js status
```

Then replace later `codex-provider ...` examples with `node src/cli.js ...` while working from that clone.

If Node.js is older than 24, stop and tell the user to install or activate Node.js 24+. Do not attempt sync with Node 20/22 because `node:sqlite` will be unavailable.

If installing requires network access, writing to a global npm prefix, or changing the user's toolchain, ask for approval according to the runtime's permission model before running the installer.

## What Sync Changes

During sync, the tool:

- Scans first-line `session_meta` records in rollout `.jsonl` files.
- Rewrites only `payload.model_provider` in rollout metadata when needed.
- Preserves rollout file modification time after rewriting.
- Updates `threads.model_provider` in `state_5.sqlite`.
- Repairs `threads.has_user_event` and `threads.cwd` when supported by the database schema and evidence exists in rollout files.
- Updates workspace root cache from thread cwd statistics.
- Creates a backup before changes and prunes old managed backups according to retention.

## What Sync Does Not Change

The tool does not:

- Log in, switch accounts, or manage `auth.json`.
- Modify message history, titles, conversation content, or `updated_at`.
- Re-encrypt `encrypted_content` for another provider/account.
- Bypass Codex Desktop's current first-page recent-session display limit.

## Status Output Interpretation

Look for:

- `Current provider`: Target for plain `sync`.
- `Configured providers`: Valid ids for `switch`.
- `Rollout files`: Provider distribution in `sessions` and `archived_sessions`.
- `SQLite state`: Provider distribution in `threads`.
- `Project visibility`: Project roots, interactive thread counts, first page counts, ranks, cwd match diagnostics, and providers.
- `encrypted_content`: Counts of rollout files containing encrypted content by provider.
- `Backups` and `Backup root`: Existing managed backup inventory.

If rollout and SQLite counts differ by provider after a provider switch, run `sync` or `switch` depending on whether config should change.

## Desktop Recent 50 Limitation

Codex Desktop may only show the first 50 recent sessions on its project side list. If status shows a project has interactive threads but `first page 0/50` or ranks outside the first page, CLI `/resume` may see sessions while Desktop still appears empty. Do not fix this by changing timestamps.

## Backup and Restore Details

Backups are stored under:

```text
~/.codex/backups_state/provider-sync/<timestamp>
```

Managed backups include:

- `metadata.json`
- `session-meta-backup.json`
- copied `state_5.sqlite` files and WAL/SHM files when present
- `config.toml` when present
- `.codex-global-state.json` files when present

Use `restore` only with backups whose `metadata.json` matches the target Codex home.

## Reporting Template

After running a command, summarize:

- Current or target provider.
- Codex home used.
- Rollout files changed and skipped.
- SQLite rows updated or whether SQLite was absent.
- Workspace roots updated, if reported.
- Backup directory, if sync or switch ran.
- Encrypted content warning, if reported.
- Backup cleanup result, if reported.
