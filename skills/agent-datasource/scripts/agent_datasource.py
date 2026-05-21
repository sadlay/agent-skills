#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "PyYAML>=6,<7",
#   "PyMySQL>=1.1,<2",
#   "psycopg[binary]>=3.2,<4",
#   "requests>=2.32,<3",
#   "neo4j>=5,<7",
# ]
# ///
"""Portable datasource runner for the agent-datasource skill."""

from __future__ import annotations

import argparse
import datetime as dt
import decimal
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import yaml


SUPPORTED_TYPES = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mysql": "mysql",
    "elasticsearch": "elasticsearch",
    "es": "elasticsearch",
    "neo4j": "neo4j",
}

SQL_READ_STARTS = ("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "WITH", "VALUES")
SQL_FORBIDDEN = {
    "INSERT", "UPDATE", "DELETE", "MERGE", "UPSERT", "REPLACE", "CREATE", "ALTER",
    "DROP", "TRUNCATE", "GRANT", "REVOKE", "COMMENT", "ANALYZE", "VACUUM", "REINDEX",
    "CLUSTER", "REFRESH", "CALL", "DO", "COPY", "LOAD", "LOCK", "UNLOCK", "SET",
    "USE", "START", "BEGIN", "COMMIT", "ROLLBACK", "EXECUTE", "PREPARE", "DEALLOCATE",
    "OPTIMIZE", "REPAIR", "FLUSH", "RESET", "KILL", "INTO",
}

CYPHER_READ_STARTS = ("MATCH", "OPTIONAL", "RETURN", "WITH", "UNWIND", "EXPLAIN", "PROFILE")
CYPHER_FORBIDDEN = {
    "CREATE", "MERGE", "SET", "DELETE", "DETACH", "REMOVE", "FOREACH", "LOAD", "DROP",
    "ALTER", "GRANT", "DENY", "REVOKE", "START", "STOP", "ENABLE", "DISABLE", "WRITE",
    "CALL",
}

ES_READ_POST_SUFFIXES = {
    "_search", "_msearch", "_count", "_mget", "_analyze", "_validate", "_explain",
    "_field_caps", "_termvectors", "_mtermvectors", "_render", "_sql", "_async_search",
    "_search_shards", "_rank_eval",
}

ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::([^}]*))?\}")


class UserError(Exception):
    """An error safe to show to the user."""


def json_default(value: Any) -> str:
    if isinstance(value, (dt.date, dt.datetime, dt.time, decimal.Decimal, bytes)):
        return str(value)
    return repr(value)


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=json_default))


def parse_bool(value: Any, *, default: bool | None = None) -> bool:
    if value is None:
        if default is None:
            raise UserError("boolean value is required")
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    raise UserError(f"invalid boolean value: {value!r}")


def resolve_env(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: resolve_env(item) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_env(item) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        default = match.group(2)
        current = os.environ.get(name)
        if current is not None:
            return current
        if default is not None:
            return default
        raise UserError(f"missing required environment variable: {name}")

    return ENV_PATTERN.sub(replace, value)


def config_candidates(path: str | None) -> list[Path]:
    if path:
        return [Path(path).expanduser()]
    env_path = os.environ.get("AGENT_DATASOURCE_CONFIG")
    if env_path:
        return [Path(env_path).expanduser()]
    root = Path.home() / ".config" / "agent-datasource"
    return [root / "datasources.yaml", root / "datasources.yml"]


def load_config(path: str | None) -> tuple[Path, list[dict[str, Any]]]:
    candidates = config_candidates(path)
    config_path = next((candidate for candidate in candidates if candidate.exists()), None)
    if config_path is None:
        raise UserError(
            "datasource config not found; checked: "
            + ", ".join(str(candidate) for candidate in candidates)
        )

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    if isinstance(raw, dict):
        sources = raw.get("datasources")
    else:
        sources = raw
    if not isinstance(sources, list):
        raise UserError("config root must be a list or contain a datasources list")

    normalized: list[dict[str, Any]] = []
    names: set[str] = set()
    for item in sources:
        if not isinstance(item, dict):
            raise UserError("each datasource entry must be an object")
        source = dict(item)
        name = str(source.get("name", "")).strip()
        raw_type = str(source.get("type", "")).strip().lower()
        if not name:
            raise UserError("each datasource requires a non-empty name")
        if name in names:
            raise UserError(f"duplicate datasource name: {name}")
        if raw_type not in SUPPORTED_TYPES:
            raise UserError(f"unsupported datasource type for {name}: {raw_type}")
        source["name"] = name
        source["type"] = SUPPORTED_TYPES[raw_type]
        normalized.append(source)
        names.add(name)
    return config_path, normalized


def user(source: dict[str, Any]) -> Any:
    return source.get("username", source.get("user"))


def require_fields(source: dict[str, Any], fields: list[str]) -> None:
    missing: list[str] = []
    for field in fields:
        if field == "username":
            if not user(source):
                missing.append("username/user")
        elif source.get(field) in (None, ""):
            missing.append(field)
    if missing:
        raise UserError(f"{source['name']} is missing required fields: {', '.join(missing)}")


def mask_url_credentials(value: Any) -> Any:
    if not isinstance(value, str) or "://" not in value or "@" not in value:
        return value
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError:
        return value
    if not parts.username and not parts.password:
        return value
    host = parts.hostname or ""
    if port is not None:
        host = f"{host}:{port}"
    return urlunsplit((parts.scheme, f"***:***@{host}", parts.path, parts.query, parts.fragment))


def safe_source(source: dict[str, Any]) -> dict[str, Any]:
    safe = {}
    for key, value in source.items():
        if key.lower() in {"password", "token", "api_key", "apikey", "secret"}:
            safe[key] = "***"
        elif key.lower() in {"url", "uri", "dsn"}:
            safe[key] = mask_url_credentials(value)
        else:
            safe[key] = value
    return safe


def find_source(sources: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for source in sources:
        if source["name"] == name:
            return source
    raise UserError(f"unknown datasource: {name}")


def strip_comments_and_literals(text: str) -> str:
    result: list[str] = []
    i = 0
    quote: str | None = None
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if quote:
            if ch == quote:
                if i + 1 < len(text) and text[i + 1] == quote:
                    i += 2
                    continue
                quote = None
            elif ch == "\\":
                i += 2
                continue
            i += 1
            continue
        if ch in {"'", '"', "`"}:
            quote = ch
            result.append(" ")
            i += 1
            continue
        if ch == "-" and nxt == "-":
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            result.append(" ")
            continue
        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            result.append(" ")
            continue
        if ch == "/" and nxt == "/":
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            result.append(" ")
            continue
        result.append(ch)
        i += 1
    return "".join(result)


def has_multiple_statements(query: str) -> bool:
    cleaned = strip_comments_and_literals(query).strip()
    parts = [part for part in cleaned.split(";") if part.strip()]
    return len(parts) > 1


def assert_read_only_sql(sql: str, allow_write: bool) -> None:
    if allow_write:
        return
    cleaned = strip_comments_and_literals(sql).strip()
    if not cleaned:
        raise UserError("SQL is empty")
    if has_multiple_statements(sql):
        raise UserError("multiple SQL statements require --allow-write")
    upper = cleaned.upper()
    if not upper.startswith(SQL_READ_STARTS):
        raise UserError("SQL is not read-only; pass --allow-write only after explicit user approval")
    tokens = set(re.findall(r"\b[A-Z_]+\b", upper))
    forbidden = sorted(tokens & SQL_FORBIDDEN)
    if forbidden:
        raise UserError(
            "SQL contains write or session keywords blocked in read-only mode: "
            + ", ".join(forbidden)
        )


def assert_read_only_cypher(cypher: str, allow_write: bool) -> None:
    if allow_write:
        return
    cleaned = strip_comments_and_literals(cypher).strip()
    if not cleaned:
        raise UserError("Cypher is empty")
    if has_multiple_statements(cypher):
        raise UserError("multiple Cypher statements require --allow-write")
    upper = cleaned.upper()
    if not upper.startswith(CYPHER_READ_STARTS):
        raise UserError("Cypher is not read-only; pass --allow-write only after explicit user approval")
    tokens = set(re.findall(r"\b[A-Z_]+\b", upper))
    forbidden = sorted(tokens & CYPHER_FORBIDDEN)
    if forbidden:
        raise UserError(
            "Cypher contains write or admin keywords blocked in read-only mode: "
            + ", ".join(forbidden)
        )


def assert_read_only_es(method: str, path: str, allow_write: bool) -> None:
    if allow_write:
        return
    method = method.upper()
    if method in {"GET", "HEAD"}:
        return
    clean_path = path.split("?", 1)[0].rstrip("/")
    suffix = clean_path.rsplit("/", 1)[-1]
    if method == "POST" and suffix in ES_READ_POST_SUFFIXES:
        return
    raise UserError("Elasticsearch request is not read-only; pass --allow-write only after explicit user approval")


def read_only_status(kind: str, *, sql: str | None = None, cypher: str | None = None,
                     method: str | None = None, path: str | None = None) -> tuple[bool, str | None]:
    try:
        if kind == "sql":
            assert_read_only_sql(sql or "", False)
        elif kind == "cypher":
            assert_read_only_cypher(cypher or "", False)
        elif kind == "elasticsearch":
            assert_read_only_es(method or "GET", path or "", False)
        else:
            raise UserError(f"unknown operation kind: {kind}")
    except UserError as exc:
        return False, str(exc)
    return True, None


def emit_dry_run(source: dict[str, Any], operation: str, allow_write: bool, preview: dict[str, Any],
                 read_only: bool, blocked_reason: str | None = None) -> None:
    emit({
        "dry_run": True,
        "source": safe_source(source),
        "operation": operation,
        "safety": {
            "allow_write": allow_write,
            "read_only": read_only,
            "blocked_without_allow_write": not read_only,
            "blocked_reason": blocked_reason,
            "requires_confirmation": allow_write,
        },
        "preview": preview,
        "would_connect": True,
        "would_execute": True,
    })


def checked_max_rows(max_rows: int) -> int:
    if max_rows < 1:
        raise UserError("--max-rows must be greater than zero")
    return max_rows


def run_postgresql(source: dict[str, Any], sql: str, max_rows: int) -> dict[str, Any]:
    import psycopg
    from psycopg.rows import dict_row

    max_rows = checked_max_rows(max_rows)
    require_fields(source, ["host", "database", "username", "password"])
    kwargs: dict[str, Any] = {
        "host": source["host"],
        "port": int(source.get("port", 5432)),
        "dbname": source["database"],
        "user": user(source),
        "password": source["password"],
        "sslmode": source.get("sslmode", "prefer"),
        "autocommit": True,
        "row_factory": dict_row,
    }
    if source.get("connect_timeout") is not None:
        kwargs["connect_timeout"] = int(source["connect_timeout"])
    if source.get("options"):
        kwargs["options"] = source["options"]
    with psycopg.connect(**kwargs) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                rows = cur.fetchmany(max_rows + 1)
                truncated = len(rows) > max_rows
                rows = rows[:max_rows]
                return {
                    "source": source["name"],
                    "type": "postgresql",
                    "row_count": len(rows),
                    "truncated": truncated,
                    "max_rows": max_rows,
                    "rows": rows,
                }
            return {"source": source["name"], "type": "postgresql", "row_count": cur.rowcount, "rows": []}


def run_mysql(source: dict[str, Any], sql: str, max_rows: int) -> dict[str, Any]:
    import pymysql
    import pymysql.cursors

    max_rows = checked_max_rows(max_rows)
    require_fields(source, ["host", "database", "username", "password"])
    kwargs: dict[str, Any] = {
        "host": source["host"],
        "port": int(source.get("port", 3306)),
        "database": source["database"],
        "user": user(source),
        "password": source["password"],
        "charset": source.get("charset", "utf8mb4"),
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
    }
    if source.get("connect_timeout") is not None:
        kwargs["connect_timeout"] = int(source["connect_timeout"])
    if source.get("ssl") is not None:
        kwargs["ssl"] = source["ssl"]
    connection = pymysql.connect(**kwargs)
    try:
        with connection.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                rows = cur.fetchmany(max_rows + 1)
                truncated = len(rows) > max_rows
                rows = rows[:max_rows]
                return {
                    "source": source["name"],
                    "type": "mysql",
                    "row_count": len(rows),
                    "truncated": truncated,
                    "max_rows": max_rows,
                    "rows": rows,
                }
            return {"source": source["name"], "type": "mysql", "row_count": cur.rowcount, "rows": []}
    finally:
        connection.close()


def run_sql_command(args: argparse.Namespace, sources: list[dict[str, Any]]) -> None:
    source = find_source(sources, args.source)
    if source["type"] not in {"postgresql", "mysql"}:
        raise UserError(f"{source['name']} is {source['type']}, not a SQL datasource")
    assert_read_only_sql(args.sql, args.allow_write)
    source = resolve_env(source)
    read_only, blocked_reason = read_only_status("sql", sql=args.sql)
    if args.dry_run:
        require_fields(source, ["host", "database", "username", "password"])
        emit_dry_run(
            source,
            "sql",
            args.allow_write,
            {"sql": args.sql, "max_rows": checked_max_rows(args.max_rows)},
            read_only,
            blocked_reason,
        )
        return
    if source["type"] == "postgresql":
        emit(run_postgresql(source, args.sql, args.max_rows))
    else:
        emit(run_mysql(source, args.sql, args.max_rows))


def parse_json_arg(value: str | None, label: str) -> Any:
    if value in (None, ""):
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise UserError(f"{label} must be valid JSON: {exc}") from exc


def run_es_command(args: argparse.Namespace, sources: list[dict[str, Any]]) -> None:
    source = find_source(sources, args.source)
    if source["type"] != "elasticsearch":
        raise UserError(f"{source['name']} is {source['type']}, not an Elasticsearch datasource")
    method = args.method.upper()
    assert_read_only_es(method, args.path, args.allow_write)
    source = resolve_env(source)
    require_fields(source, ["url"])
    params = parse_json_arg(args.params, "--params")
    body = parse_json_arg(args.body, "--body")
    read_only, blocked_reason = read_only_status("elasticsearch", method=method, path=args.path)
    if args.dry_run:
        emit_dry_run(
            source,
            "elasticsearch",
            args.allow_write,
            {"method": method, "path": args.path, "params": params, "body": body},
            read_only,
            blocked_reason,
        )
        return

    import requests

    url = str(source["url"]).rstrip("/") + "/" + args.path.lstrip("/")
    auth = None
    if user(source) or source.get("password"):
        auth = (user(source), source.get("password", ""))
    response = requests.request(
        method,
        url,
        params=params,
        json=body,
        auth=auth,
        verify=parse_bool(source.get("verify_tls"), default=True),
        timeout=float(source.get("timeout", 30)),
    )
    output: dict[str, Any] = {
        "source": source["name"],
        "type": "elasticsearch",
        "status_code": response.status_code,
        "ok": response.ok,
    }
    try:
        output["body"] = response.json()
    except ValueError:
        output["text"] = response.text
    emit(output)
    if not response.ok:
        raise SystemExit(2)


def run_cypher_command(args: argparse.Namespace, sources: list[dict[str, Any]]) -> None:
    source = find_source(sources, args.source)
    if source["type"] != "neo4j":
        raise UserError(f"{source['name']} is {source['type']}, not a Neo4j datasource")
    assert_read_only_cypher(args.cypher, args.allow_write)
    max_rows = checked_max_rows(args.max_rows)
    source = resolve_env(source)
    require_fields(source, ["uri", "username", "password"])
    read_only, blocked_reason = read_only_status("cypher", cypher=args.cypher)
    if args.dry_run:
        emit_dry_run(
            source,
            "cypher",
            args.allow_write,
            {"cypher": args.cypher, "max_rows": max_rows},
            read_only,
            blocked_reason,
        )
        return

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(source["uri"], auth=(user(source), source["password"]))
    try:
        with driver.session(database=source.get("database", "neo4j")) as session:
            result = session.run(args.cypher)
            rows = []
            truncated = False
            for record in result:
                if len(rows) >= max_rows:
                    truncated = True
                    break
                rows.append(record.data())
        emit({
            "source": source["name"],
            "type": "neo4j",
            "row_count": len(rows),
            "truncated": truncated,
            "max_rows": max_rows,
            "rows": rows,
        })
    finally:
        driver.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run configured datasource operations.")
    parser.add_argument("--config", help="Path to datasource YAML. Overrides AGENT_DATASOURCE_CONFIG.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List configured datasources without secrets.")
    list_parser.add_argument("--type", choices=sorted(set(SUPPORTED_TYPES.values())), help="Filter by datasource type.")

    subparsers.add_parser("check-env", help="Show resolved config path and datasource count.")

    sql_parser = subparsers.add_parser("sql", help="Run SQL against PostgreSQL or MySQL.")
    sql_parser.add_argument("--source", required=True)
    sql_parser.add_argument("--sql", required=True)
    sql_parser.add_argument("--max-rows", type=int, default=1000)
    sql_parser.add_argument("--allow-write", action="store_true")
    sql_parser.add_argument("--dry-run", action="store_true", help="Preview source, operation, and safety without connecting.")

    es_parser = subparsers.add_parser("es", help="Run Elasticsearch REST DSL request.")
    es_parser.add_argument("--source", required=True)
    es_parser.add_argument("--method", default="GET")
    es_parser.add_argument("--path", required=True)
    es_parser.add_argument("--params", help="JSON object for query parameters.")
    es_parser.add_argument("--body", help="JSON request body.")
    es_parser.add_argument("--allow-write", action="store_true")
    es_parser.add_argument("--dry-run", action="store_true", help="Preview source, operation, and safety without connecting.")

    cypher_parser = subparsers.add_parser("cypher", help="Run Cypher against Neo4j.")
    cypher_parser.add_argument("--source", required=True)
    cypher_parser.add_argument("--cypher", required=True)
    cypher_parser.add_argument("--max-rows", type=int, default=1000)
    cypher_parser.add_argument("--allow-write", action="store_true")
    cypher_parser.add_argument("--dry-run", action="store_true", help="Preview source, operation, and safety without connecting.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path, sources = load_config(args.config)

    if args.command == "list":
        visible = [safe_source(source) for source in sources if not args.type or source["type"] == args.type]
        emit({"config": str(config_path), "count": len(visible), "datasources": visible})
        return 0
    if args.command == "check-env":
        emit({"config": str(config_path), "count": len(sources), "types": sorted({source["type"] for source in sources})})
        return 0
    if args.command == "sql":
        run_sql_command(args, sources)
        return 0
    if args.command == "es":
        run_es_command(args, sources)
        return 0
    if args.command == "cypher":
        run_cypher_command(args, sources)
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UserError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
