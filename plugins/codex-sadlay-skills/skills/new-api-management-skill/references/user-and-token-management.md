# User And Token Management

Use this for official user-management, token-management, and group APIs, plus access troubleshooting.

## Users

List/search/read:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/user/?p=1&page_size=100" | jq .
```

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/user/search?keyword=liyaping" | jq .
```

- `GET /api/user/:id`
- `POST /api/user/`
- `PUT /api/user/`
- `POST /api/user/manage`
- `DELETE /api/user/:id`

When updating users, fetch the current record first and preserve unrelated fields.

Self checks:

- `GET /api/user/self`
- `GET /api/user/models`
- `GET /api/user/self/groups`
- `PUT /api/user/self`

## API Tokens

List/search/read:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/token/?p=1&page_size=100" | jq .
```

- `GET /api/token/search`
- `GET /api/token/:id`
- `POST /api/token/`
- `PUT /api/token/`
- `DELETE /api/token/:id`
- `POST /api/token/batch`

Sensitive key reveal endpoints:

- `POST /api/token/:id/key`
- `POST /api/token/batch/keys`

Only call key reveal endpoints when the user explicitly asks and has an operational need.

## Groups

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/group/" | jq .
```

Groups affect model availability, channel routing, token limits, and pricing. For "user cannot use model" issues, compare:

- user status and group
- token status, group, and model limits
- channel group coverage
- `/api/channel/models_enabled`
- `/api/pricing`

## Token-Auth Usage Lookup

Read-only API-key usage endpoint:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $SK_KEY" \
  "$NEWAPI_BASE_URL/api/usage/token/" | jq .
```

Use `sk-*` only for token-auth endpoints, not dashboard/admin management APIs.
