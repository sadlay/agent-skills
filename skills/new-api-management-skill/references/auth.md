# Auth

Use this for authentication, headers, and permission checks before any live New API management operation.

## Required Headers

Management APIs use a user access token:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/user/self" | jq .
```

`New-Api-User` must match the user id bound to the access token. Missing or mismatched values commonly produce 401 responses.

Relay/model-call APIs use `sk-*` API keys, not the management access token.

## Permission Levels

- Root/admin token: system options, ratio maps, sensitive channel key reads, model and vendor management.
- Admin token: users, channels, logs, groups, vendors, model metadata, prefill groups.
- User token: self profile, own API keys, own logs/statistics.
- API key (`sk-*`): `/v1/*` relay calls and token-auth read-only usage endpoints.

## Identity Checks

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/user/self" | jq .
```

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/status/test" | jq .
```

## Common Mistakes

- Do not print or paste access tokens in final answers.
- Do not use `sk-*` keys for `/api/user`, `/api/channel`, `/api/models`, `/api/option`, or `/api/log/stat`.
- Do not use the management access token for `/v1/chat/completions`, `/v1/responses`, or `/v1/embeddings`.
