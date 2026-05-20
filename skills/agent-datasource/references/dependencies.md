# Dependency Guidance

Preferred execution uses `uv run` directly against the bundled script:

```bash
uv run scripts/agent_datasource.py check-env
```

The script declares inline dependencies, so `uv` resolves them automatically in an isolated environment.

## Required Python Packages

- PostgreSQL: `psycopg[binary]>=3.2,<4`
- MySQL: `PyMySQL>=1.1,<2`
- Elasticsearch: `requests>=2.32,<3`
- Neo4j: `neo4j>=5,<7`
- YAML config: `PyYAML>=6,<7`

## Environment Check

Run this from the skill directory:

```bash
python3 scripts/check_env.py
```

This diagnostic is standard-library only. It checks Python version, `uv` availability, config path, and whether drivers are importable in the current Python environment.

## Manual Installation

Use manual installation only when `uv` is unavailable or a fixed Python environment is required:

```bash
python3 -m pip install "psycopg[binary]>=3.2,<4" "PyMySQL>=1.1,<2" "requests>=2.32,<3" "neo4j>=5,<7" "PyYAML>=6,<7"
```

Drivers are generally compatible across common server versions:

- `PyMySQL` works with MySQL 5.x and 8.x for typical SQL operations.
- `psycopg[binary]` is psycopg 3 with bundled libpq and works across supported PostgreSQL versions.
- `requests` uses Elasticsearch REST APIs and avoids a strict client/server version lock for common DSL calls.
- `neo4j` supports Neo4j Bolt connections; keep the driver reasonably current for newer Neo4j servers.
