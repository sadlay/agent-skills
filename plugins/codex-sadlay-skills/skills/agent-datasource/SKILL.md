---
name: agent-datasource
description: Use when an agent needs to discover, query, or inspect configured PostgreSQL, MySQL, Elasticsearch, or Neo4j data sources from a portable YAML datasource registry with safe read-only defaults and explicit write opt-in.
---

# Agent Datasource

Use this skill to work with configured data sources through a portable YAML registry. Prefer the bundled Python runner instead of MCP Toolbox when the user wants one reusable skill across many machines and data sources.

Resolve `scripts/`, `references/`, and `assets/` paths relative to this skill directory. If running commands manually, `cd` into the installed `agent-datasource` skill directory first or use an absolute path to the bundled script.

## Default Workflow

1. Locate the datasource config:
   - Use `AGENT_DATASOURCE_CONFIG` when set.
   - Otherwise use `~/.config/agent-datasource/datasources.yaml`.
   - If missing, also check `~/.config/agent-datasource/datasources.yml`.
2. If the environment is uncertain, run:

```bash
python3 scripts/check_env.py
```

3. List configured sources before querying unless the user explicitly named a source:

```bash
uv run scripts/agent_datasource.py list
```

4. Choose one or more sources by `name`, `type`, and especially `description`. Use `description` as the routing hint for business domain, covered entities, environment, freshness, and common use cases.
   - If multiple sources may be needed, start with the source most likely to identify the primary entity, query narrowly, then use returned identifiers to query related sources.
   - If descriptions are ambiguous or multiple sources look equally relevant, ask the user to choose before querying.
5. Choose the command by source type:
   - PostgreSQL/MySQL: `sql`
   - Elasticsearch: `es`
   - Neo4j: `cypher`
6. Before writing task-specific queries, perform narrow schema discovery unless the user already provided the relevant schema.
7. Keep operations read-only unless the user explicitly asks for a write. Writes require `--allow-write`.
8. For writes, first run the intended command with `--dry-run --allow-write`, show the preview to the user, ask for confirmation, then rerun without `--dry-run` only after explicit approval.

## Commands

List sources:

```bash
uv run scripts/agent_datasource.py list
uv run scripts/agent_datasource.py list --type mysql
```

Run SQL against PostgreSQL or MySQL:

```bash
uv run scripts/agent_datasource.py sql --source my-mysql --sql "select * from users limit 10"
uv run scripts/agent_datasource.py sql --source my-postgres --sql "select * from events" --max-rows 100
uv run scripts/agent_datasource.py sql --source my-mysql --sql "update refunds set status = 'reviewed' where id = 1" --allow-write --dry-run
```

Run Elasticsearch DSL through REST:

```bash
uv run scripts/agent_datasource.py es --source my-es --method POST --path /my-index/_search --body '{"query":{"match_all":{}},"size":10}'
uv run scripts/agent_datasource.py es --source my-es --method DELETE --path /old-index --allow-write --dry-run
```

Run Neo4j Cypher:

```bash
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "MATCH (n) RETURN n LIMIT 10"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "MATCH (n:Temp) DELETE n" --allow-write --dry-run
```

Use a non-default config file:

```bash
AGENT_DATASOURCE_CONFIG=/path/to/datasources.yaml uv run scripts/agent_datasource.py list
uv run scripts/agent_datasource.py --config /path/to/datasources.yaml list
```

## Schema Discovery

Use read-only metadata queries to understand the datasource before writing task-specific queries. Keep discovery narrow: list candidate structures first, then inspect only the tables, indexes, labels, or relationship types that matter.

PostgreSQL/MySQL table discovery:

```bash
uv run scripts/agent_datasource.py sql --source my-mysql --sql "select table_schema, table_name from information_schema.tables where table_schema not in ('information_schema', 'pg_catalog', 'mysql', 'performance_schema', 'sys') order by table_schema, table_name limit 100"
```

PostgreSQL/MySQL column discovery:

```bash
uv run scripts/agent_datasource.py sql --source my-mysql --sql "select table_schema, table_name, column_name, data_type, is_nullable from information_schema.columns where table_name = 'users' order by ordinal_position"
```

Elasticsearch index and mapping discovery:

```bash
uv run scripts/agent_datasource.py es --source my-es --method GET --path "/_cat/indices?format=json"
uv run scripts/agent_datasource.py es --source my-es --method GET --path "/my-index/_mapping"
```

Neo4j schema discovery:

```bash
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "CALL db.schema.visualization()"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "CALL db.schema.nodeTypeProperties()"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "CALL db.schema.relTypeProperties()"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "CALL db.labels()"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "CALL db.relationshipTypes()"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "CALL db.propertyKeys()"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "SHOW INDEXES"
uv run scripts/agent_datasource.py cypher --source my-neo4j --cypher "SHOW CONSTRAINTS"
```

`CALL db.schema.visualization()` returns a virtual schema graph for overview. Use `db.schema.nodeTypeProperties()` and `db.schema.relTypeProperties()` when property names and types matter.

## Configuration

Use [configuration.md](references/configuration.md) when creating or changing datasource YAML. The bundled example is at [datasources.example.yaml](assets/datasources.example.yaml).

Write `description` for agent routing, not only for human documentation. Include the business domain, major entities, environment, freshness, and typical questions. Example: `Production MySQL for orders, payments, refunds, invoices, and settlement records. Use for customer transaction questions.`

The config may be a list or an object with a `datasources` list. Values support environment placeholders:

```yaml
datasources:
  - name: my-mysql
    type: mysql
    description: Example MySQL database
    host: ${MYSQL_HOST:localhost}
    port: ${MYSQL_PORT:3306}
    database: ${MYSQL_DATABASE}
    username: ${MYSQL_USER}
    password: ${MYSQL_PASSWORD}
```

## Dependencies

The runner uses `uv run` with inline Python dependencies:

- `psycopg[binary]` for PostgreSQL
- `PyMySQL` for MySQL
- `requests` for Elasticsearch
- `neo4j` for Neo4j
- `PyYAML` for config loading

Read [dependencies.md](references/dependencies.md) when dependencies are missing, `uv` is unavailable, or a machine needs manual installation guidance.

## Safety Rules

- Never print passwords, tokens, or full connection strings.
- Default to read-only. Do not pass `--allow-write` unless the user explicitly requests a write operation.
- Before any write, run the exact intended command with `--dry-run --allow-write`, show the preview, and wait for explicit user confirmation.
- For SQL and Cypher, inspect the query intent before executing. The runner blocks common write keywords, but the agent is still responsible for avoiding unsafe operations.
- For Elasticsearch, prefer `POST /<index>/_search` with a DSL body for searches. Avoid destructive methods unless explicitly requested.
- SQL and Cypher default to `--max-rows 1000`; lower it for exploratory queries. Report the source name, source type, query shape, row or hit count, and any truncation.
