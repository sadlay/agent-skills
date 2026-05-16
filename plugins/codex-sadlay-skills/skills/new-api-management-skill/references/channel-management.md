# Channel Management

Use this for official channel-management APIs, routing coverage, upstream model detection, and channel health.

## List/Search/Read

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/channel/?p=1&page_size=1000" | jq .
```

- `GET /api/channel/search`
- `GET /api/channel/:id`
- `GET /api/channel/models`
- `GET /api/channel/models_enabled`
- `GET /api/channel/tag/models`

Useful fields usually include `id`, `name`, `type`, `status`, `models`, `group`, `priority`, `weight`, `balance`, `used_quota`, and `tag`.

## Create/Update/Delete

- `POST /api/channel/`
- `PUT /api/channel/`
- `DELETE /api/channel/:id`
- `DELETE /api/channel/disabled`
- `POST /api/channel/batch`
- `POST /api/channel/copy/:id`
- `POST /api/channel/fix`

Fetch a channel before updating and preserve unrelated fields.

## Tag And Batch Operations

- `POST /api/channel/tag/disabled`
- `POST /api/channel/tag/enabled`
- `PUT /api/channel/tag`
- `POST /api/channel/batch/tag`

Use tag operations only after listing matching channels and confirming the intended scope.

## Tests And Balances

Test all channels:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/channel/test" | jq .
```

Test one channel:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/channel/test/123" | jq .
```

Balances:

- `GET /api/channel/update_balance`
- `GET /api/channel/update_balance/:id`

Channel tests and balance updates may call upstream providers and can consume quota or trigger rate limits.

## Upstream Model Changes

Detect:

- `POST /api/channel/upstream_updates/detect`
- `POST /api/channel/upstream_updates/detect_all`

Apply:

- `POST /api/channel/upstream_updates/apply`
- `POST /api/channel/upstream_updates/apply_all`

Apply only after reviewing detected additions/removals.

## Health Audit

1. Read `/api/channel/` for disabled/error channels.
2. Read `/api/channel/models_enabled` and compare with `/api/pricing`.
3. Check models with only one enabled channel if availability matters.
4. Check recent error logs with `/api/log/?type=5`.
5. Run channel tests only when the user accepts possible upstream traffic/cost.
