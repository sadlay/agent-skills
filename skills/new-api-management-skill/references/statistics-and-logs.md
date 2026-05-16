# Statistics And Logs

Use this for official logs and statistics APIs, including user/model/token/channel usage reports.

## Time Window

```bash
START=$(date -v-7d +%s 2>/dev/null || date -d '7 days ago' +%s)
END=$(date +%s)
```

## Log Statistics

Admin summary:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/log/stat?type=2&start_timestamp=$START&end_timestamp=$END" | jq .
```

Self summary:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/log/self/stat?type=2&start_timestamp=$START&end_timestamp=$END" | jq .
```

Useful filters include `username`, `model_name`, `token_name`, `channel`, and `group`. `type=2` is consumption logs.

## Raw Logs

Admin:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/log/?type=2&p=1&page_size=100&start_timestamp=$START&end_timestamp=$END" | jq .
```

Other log endpoints:

- `GET /api/log/search`
- `GET /api/log/self`
- `GET /api/log/self/search`
- `DELETE /api/log/`
- `GET /api/log/channel_affinity_usage_cache`
- `GET /api/log/token` with `sk-*` token auth

Do not delete logs unless the user explicitly requests it.

## Aggregation With jq

Top models:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/log/?type=2&p=1&page_size=1000&start_timestamp=$START&end_timestamp=$END" |
jq '[.data.items[]]
  | group_by(.model_name)
  | map({model:.[0].model_name, requests:length, quota:(map(.quota // 0)|add), prompt:(map(.prompt_tokens // 0)|add), completion:(map(.completion_tokens // 0)|add)})
  | sort_by(.quota) | reverse'
```

Top users:

```bash
jq '[.data.items[]]
  | group_by(.username)
  | map({username:.[0].username, requests:length, quota:(map(.quota // 0)|add), tokens:(map((.prompt_tokens // 0)+(.completion_tokens // 0))|add)})
  | sort_by(.quota) | reverse'
```

If one page is insufficient, page through `p=` until `p * page_size >= data.total`.

## Data Statistics

Quota/date statistics:

- `GET /api/data/`
- `GET /api/data/users`
- `GET /api/data/self`

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/data/" | jq .
```

## Cost Estimate

Fetch `QuotaPerUnit`:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/option/" |
jq -r '.data[] | select(.key=="QuotaPerUnit") | .value'
```

Estimated cost is usually `quota / QuotaPerUnit`. Report it as estimated unless the site's quota-to-currency policy is confirmed.
