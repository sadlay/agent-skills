# Model Management

Use this for official model-management APIs plus adjacent vendor and pricing touchpoints needed to maintain model metadata.

## Effective Model Catalog

`/api/pricing` is the effective catalog assembled from enabled channel abilities, model metadata, vendors, and pricing settings.

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS "$NEWAPI_BASE_URL/api/pricing" | jq .
```

Audit missing metadata:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS "$NEWAPI_BASE_URL/api/pricing" |
jq '.data[] | select((.description // "") == "" or (.tags // "") == "") | {model_name,vendor_id,description,tags,model_ratio,completion_ratio,supported_endpoint_types}'
```

## Model Metadata

List:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/models/?p=1&page_size=10000" | jq .
```

Search and read:

- `GET /api/models/search`
- `GET /api/models/:id`
- `GET /api/models/missing`

Create/update/delete:

- `POST /api/models/`
- `PUT /api/models/`
- `DELETE /api/models/:id`

For updates, fetch the current model record first, preserve unrelated fields, and send the full expected payload.

Typical payload:

```json
{
  "id": 123,
  "model_name": "example-model",
  "description": "简短、可搜索的中文能力描述。",
  "icon": "OpenAI",
  "tags": "文本,推理,编程,工具调用",
  "vendor_id": 37,
  "endpoints": "{\"openai\":{\"path\":\"/v1/chat/completions\",\"method\":\"POST\"}}",
  "status": 1,
  "sync_official": 0,
  "name_rule": 0
}
```

Set `sync_official=0` for manually curated metadata.

## Endpoint Presets

Chat and reasoning:

```json
{
  "openai": {"path": "/v1/chat/completions", "method": "POST"},
  "openai-response": {"path": "/v1/responses", "method": "POST"},
  "anthropic": {"path": "/v1/messages", "method": "POST"}
}
```

Other common endpoints:

```json
{
  "embeddings": {"path": "/v1/embeddings", "method": "POST"},
  "jina-rerank": {"path": "/v1/rerank", "method": "POST"},
  "image-generation": {"path": "/v1/images/generations", "method": "POST"}
}
```

## Official Sync

Preview:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/models/sync_upstream/preview?locale=zh" | jq .
```

Apply:

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS -X POST \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  -H "Content-Type: application/json" \
  -d '{"locale":"zh"}' \
  "$NEWAPI_BASE_URL/api/models/sync_upstream" | jq .
```

The built-in upstream source is a New API metadata preset, not provider-official truth. For pricing and capability-sensitive changes, verify against provider official docs.

## Vendors

Vendor APIs are separate in the official management docs but are needed for model metadata.

```bash
curl ${NEWAPI_INSECURE_TLS:+-k} -sS \
  -H "Authorization: Bearer $NEWAPI_ACCESS_TOKEN" \
  -H "New-Api-User: ${NEWAPI_USER_ID:-1}" \
  "$NEWAPI_BASE_URL/api/vendors/" | jq .
```

CRUD:

- `GET /api/vendors/search`
- `GET /api/vendors/:id`
- `POST /api/vendors/`
- `PUT /api/vendors/`
- `DELETE /api/vendors/:id`

## Pricing Touchpoint

Model ratios and fixed prices are stored under system options, not the model metadata endpoint. Use [system-options.md](system-options.md) for `ModelRatio`, `CompletionRatio`, `CacheRatio`, `ImageRatio`, `ModelPrice`, and related maps.
