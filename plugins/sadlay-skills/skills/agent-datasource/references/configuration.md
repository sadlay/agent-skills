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
- `description`: Optional but strongly recommended. Write this for agent routing: include business domain, major entities, environment, freshness, and typical questions.
- `username` or `user`: Login user when required.
- `password`: Login password when required.

String values support environment placeholders:

- `${ENV_NAME}`: require `ENV_NAME`.
- `${ENV_NAME:default}`: use default when `ENV_NAME` is unset.

Good description example:

```yaml
description: Production MySQL for orders, payments, refunds, invoices, and settlement records. Use for customer transaction questions.
```

Avoid vague descriptions such as `production database` or `main datasource`; they make source selection harder for agents.

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

Schema discovery:

```bash
uv run scripts/agent_datasource.py sql --source analytics-postgres --sql "select table_schema, table_name from information_schema.tables where table_schema not in ('information_schema', 'pg_catalog') order by table_schema, table_name limit 100"
uv run scripts/agent_datasource.py sql --source analytics-postgres --sql "select table_schema, table_name, column_name, data_type, is_nullable from information_schema.columns where table_name = 'events' order by ordinal_position"
```

Write preview:

```bash
uv run scripts/agent_datasource.py sql --source analytics-postgres --sql "update events set reviewed = true where id = 123" --allow-write --dry-run
```

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

Schema discovery:

```bash
uv run scripts/agent_datasource.py sql --source metadata-mysql --sql "select table_schema, table_name from information_schema.tables where table_schema not in ('information_schema', 'mysql', 'performance_schema', 'sys') order by table_schema, table_name limit 100"
uv run scripts/agent_datasource.py sql --source metadata-mysql --sql "select table_schema, table_name, column_name, data_type, is_nullable from information_schema.columns where table_name = 'users' order by ordinal_position"
```

Write preview:

```bash
uv run scripts/agent_datasource.py sql --source metadata-mysql --sql "update users set status = 'disabled' where id = 123" --allow-write --dry-run
```

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

Schema discovery:

```bash
uv run scripts/agent_datasource.py es --source search-prod --method GET --path "/_cat/indices?format=json"
uv run scripts/agent_datasource.py es --source search-prod --method GET --path "/my-index/_mapping"
```

Write preview:

```bash
uv run scripts/agent_datasource.py es --source search-prod --method DELETE --path "/old-index" --allow-write --dry-run
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

Schema discovery:

```bash
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "CALL db.schema.visualization()"
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "CALL db.schema.nodeTypeProperties()"
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "CALL db.schema.relTypeProperties()"
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "CALL db.labels()"
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "CALL db.relationshipTypes()"
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "CALL db.propertyKeys()"
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "SHOW INDEXES"
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "SHOW CONSTRAINTS"
```

`CALL db.schema.visualization()` is useful for a structural overview. It returns a virtual schema graph, not business nodes. Use `db.schema.nodeTypeProperties()` and `db.schema.relTypeProperties()` for property names and types.

Write preview:

```bash
uv run scripts/agent_datasource.py cypher --source graph-test --cypher "MATCH (n:Temp) DELETE n" --allow-write --dry-run
```
