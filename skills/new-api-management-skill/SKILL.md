---
name: new-api-management-skill
description: Use when managing a live New API instance through management REST APIs, especially model management, user and token administration, usage statistics, logs, channels, vendors, groups, pricing options, and health audits.
---

# New API Management Skill

Use this skill to operate a running New API instance through management REST APIs. Do not modify source code unless the user explicitly asks for source changes.

## Required Environment

Before any live operation, require:

```bash
export NEWAPI_BASE_URL="https://your-new-api.example.com"
export NEWAPI_ACCESS_TOKEN="..."
```

Optional:

```bash
export NEWAPI_USER_ID="1"          # default root/admin user id
export NEWAPI_INSECURE_TLS="1"     # use curl -k for internal/self-signed HTTPS
```

If `NEWAPI_BASE_URL` or `NEWAPI_ACCESS_TOKEN` is missing, stop and ask the user to set it. Never print the token. If the environment still uses historical `NEW_API_*` names, map them to `NEWAPI_*` before calling APIs.

## REST Call Pattern

Use direct REST calls. Prefer `curl` plus `jq` for inspection and small updates:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/pricing" | jq .
```

For updates, fetch current state first, merge only the intended keys, write back, then verify through a fresh GET. Do not replace whole JSON option maps from memory.

## Reference Navigation

The reference layout follows the official management-interface grouping. Load only the file needed for the user’s task:

- Auth and permission rules: [auth.md](references/auth.md)
- Model metadata, vendors, official sync, pricing touchpoints: [model-management.md](references/model-management.md)
- Users, API keys, groups, access troubleshooting: [user-and-token-management.md](references/user-and-token-management.md)
- Usage statistics, logs, user/model/token reports: [statistics-and-logs.md](references/statistics-and-logs.md)
- Channels, routing coverage, upstream model detection, health tests: [channel-management.md](references/channel-management.md)
- System options, pricing ratio maps, backup, performance maintenance: [system-options.md](references/system-options.md)

Official New API docs entrypoint: `https://docs.newapi.pro/zh/docs/api`, especially the "管理接口" section. When source and docs differ, prefer source for the deployed project behavior and mention the discrepancy.

## Safety Rules

- Treat the access token as a secret.
- Use the user access token for dashboard/admin APIs; use `sk-*` API keys only for relay/model-call APIs.
- Avoid payment/subscription automation unless the user explicitly requests it.
- Check New API official docs first for management API shape; browse provider official docs before changing prices or capability metadata for modern models.
- Keep changes scoped to the requested models, channels, users, or time window.
- After every write, verify with a fresh GET and report the concrete result.
