# Datasource Configuration

The default config location is `~/.config/agent-datasource/datasources.yaml`. `datasources.yml` is accepted as a fallback. `AGENT_DATASOURCE_CONFIG` may point to any exact config file path.

The root may be either:

```yaml
datasources:
  - name: example
    type: mysql
```

or:

```yaml
- name: example
  type: mysql
```

## Shared Fields

- `name`: Required unique datasource name. Use this with `--source`.
- `type`: Required. Supported values: `postgresql`, `postgres`, `mysql`, `elasticsearch`, `es`, `neo4j`.
- `description`: Optional human-readable description.
- `username` or `user`: Login user when required.
- `password`: Login password when required.

String values support environment placeholders:

- `${ENV_NAME}`: require `ENV_NAME`.
- `${ENV_NAME:default}`: use default when `ENV_NAME` is unset.

## PostgreSQL

```yaml
- name: analytics-postgres
  type: postgresql
  description: Business analytics PostgreSQL
  host: ${ANALYTICS_PG_HOST}
  port: ${ANALYTICS_PG_PORT:5432}
  database: ${ANALYTICS_PG_DATABASE}
  username: ${ANALYTICS_PG_USER}
  password: ${ANALYTICS_PG_PASSWORD}
  sslmode: ${ANALYTICS_PG_SSLMODE:prefer}
  connect_timeout: 10
```

Required: `host`, `database`, `username` or `user`, `password`.

Optional: `port` default `5432`, `sslmode` default `prefer`, `connect_timeout`, `options`.

## MySQL

```yaml
- name: metadata-mysql
  type: mysql
  description: Metadata MySQL
  host: ${METADATA_MYSQL_HOST}
  port: ${METADATA_MYSQL_PORT:3306}
  database: ${METADATA_MYSQL_DATABASE}
  username: ${METADATA_MYSQL_USER}
  password: ${METADATA_MYSQL_PASSWORD}
  charset: utf8mb4
  connect_timeout: 10
```

Required: `host`, `database`, `username` or `user`, `password`.

Optional: `port` default `3306`, `charset` default `utf8mb4`, `connect_timeout`, `ssl`.

## Elasticsearch

```yaml
- name: search-prod
  type: elasticsearch
  description: Search cluster
  url: ${SEARCH_ES_URL}
  username: ${SEARCH_ES_USER}
  password: ${SEARCH_ES_PASSWORD}
  verify_tls: true
  timeout: 30
```

Required: `url`. `username` and `password` are optional only when the cluster allows anonymous access.

Optional: `verify_tls` default `true`, `timeout` default `30`.

Use REST DSL for searches:

```bash
uv run scripts/agent_datasource.py es --source search-prod --method POST --path /my-index/_search --body '{"query":{"match_all":{}},"size":10}'
```

## Neo4j

```yaml
- name: graph-test
  type: neo4j
  description: Graph database
  uri: ${GRAPH_NEO4J_URI:bolt://localhost:7687}
  username: ${GRAPH_NEO4J_USER}
  password: ${GRAPH_NEO4J_PASSWORD}
  database: ${GRAPH_NEO4J_DATABASE:neo4j}
```

Required: `uri`, `username` or `user`, `password`.

Optional: `database` default `neo4j`.
