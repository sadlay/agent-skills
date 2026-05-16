# System Options

Use this for official system and system-settings APIs that support model pricing, backup, and maintenance.

## Status

Public:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS "$NEWAPI_BASE_URL/api/status" | jq .
curl ${NEWAPI_INSECURE_TLS:+-k} -sS "$NEWAPI_BASE_URL/api/notice" | jq .
curl ${NEWAPI_INSECURE_TLS:+-k} -sS "$NEWAPI_BASE_URL/api/about" | jq .
```

Admin:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/status/test" | jq .
```

## Options

Read all:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/option/" | jq .
```

Update one option:

```bash
jq -n --arg key "OptionKey" --arg value "OptionValue" '{key:$key,value:$value}' > /tmp/newapi-option-update.json
curl ${NEWAPI_INSECURE_TLS:+-k} -sS -X PUT \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  -H "Content-Type: application/json" \
  -d @/tmp/newapi-option-update.json \
  "$NEWAPI_BASE_URL/api/option/" | jq .
```

For JSON-valued options, fetch the current value, parse it with `jq`, merge intended keys, and write back compact JSON.

## Model Pricing Option Maps

Common keys:

- `ModelRatio`
- `CompletionRatio`
- `CacheRatio`
- `ImageRatio`
- `AudioRatio`
- `AudioCompletionRatio`
- `ModelPrice`
- `CreateCacheRatio`
- `QuotaPerUnit`

Conversion convention for token-priced models:

```text
model_ratio      = input_usd_per_1m / 2
completion_ratio = output_usd_per_1m / input_usd_per_1m
cache_ratio      = cached_input_usd_per_1m / input_usd_per_1m
image_ratio      = image_input_usd_per_1m / text_input_usd_per_1m
```

For per-request image/video/task models, use `ModelPrice` instead of token ratios.

Verify via:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS "$NEWAPI_BASE_URL/api/pricing" |
jq '.data[] | select(.model_name=="example-model")'
```

## Reset And Cache Maintenance

- `POST /api/option/rest_model_ratio`
- `GET /api/option/channel_affinity_cache`
- `DELETE /api/option/channel_affinity_cache`
- `POST /api/option/migrate_console_setting`

Create a backup before reset or migration endpoints.

## Backup

```bash
mkdir -p backups
TS=$(date +%Y%m%d-%H%M%S)

for path in \
  "option/" \
  "models/?p=1&page_size=10000" \
  "vendors/" \
  "channel/?p=1&page_size=10000" \
  "user/?p=1&page_size=10000" \
  "token/?p=1&page_size=10000" \
  "group/"
do
  name=$(printf "%s" "$path" | tr '/?=&' '____')
  curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
    -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
    -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
    "$NEWAPI_BASE_URL/api/$path" > "backups/${name}-${TS}.json"
done
```

Restore one resource class at a time and verify after each write.

## Performance Maintenance

- `GET /api/performance/stats`
- `GET /api/performance/logs`
- `DELETE /api/performance/logs`
- `DELETE /api/performance/disk_cache`
- `POST /api/performance/reset_stats`
- `POST /api/performance/gc`

Do not clear logs, caches, or stats unless the user explicitly requests it.
