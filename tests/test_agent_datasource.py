from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import sys
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "agent-datasource" / "scripts" / "agent_datasource.py"


def load_runner():
    if "yaml" not in sys.modules:
        yaml_stub = types.ModuleType("yaml")

        def safe_load(value):
            if hasattr(value, "read"):
                value = value.read()
            return json.loads(value)

        yaml_stub.safe_load = safe_load
        sys.modules["yaml"] = yaml_stub
    spec = importlib.util.spec_from_file_location("agent_datasource", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AgentDatasourceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = load_runner()
        self.tempdir = tempfile.TemporaryDirectory()
        self.config = Path(self.tempdir.name) / "datasources.yaml"
        self.config.write_text(
            json.dumps(
                {
                    "datasources": [
                        {
                            "name": "order-mysql",
                            "type": "mysql",
                            "description": "Production MySQL for orders, payments, refunds, invoices, and settlement records. Use for customer transaction questions.",
                            "host": "mysql.example.internal",
                            "port": 3306,
                            "database": "orders",
                            "username": "order_reader",
                            "password": "super-secret",
                        },
                        {
                            "name": "logs-es",
                            "type": "elasticsearch",
                            "description": "Production Elasticsearch for application logs, request traces, and error investigations.",
                            "url": "https://elastic:secret@example.internal:9200",
                            "verify_tls": True,
                        },
                        {
                            "name": "graph-neo4j",
                            "type": "neo4j",
                            "description": "Graph database for account relationships, ownership links, and organization topology.",
                            "uri": "bolt://neo4j.example.internal:7687",
                            "username": "neo4j",
                            "password": "graph-secret",
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_main(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = self.runner.main(["--config", str(self.config), *args])
            except SystemExit as exc:
                code = int(exc.code)
            except self.runner.UserError as exc:
                print(f"error: {exc}", file=stderr)
                code = 2
        return code, stdout.getvalue(), stderr.getvalue()

    def test_list_masks_secrets_and_preserves_descriptions(self) -> None:
        code, stdout, stderr = self.run_main("list")

        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["count"], 3)
        mysql = payload["datasources"][0]
        es = payload["datasources"][1]
        self.assertEqual(mysql["password"], "***")
        self.assertEqual(es["url"], "https://***:***@example.internal:9200")
        self.assertIn("orders, payments, refunds", mysql["description"])

    def test_write_sql_without_allow_write_is_blocked_before_connecting(self) -> None:
        def fail_connect(*_args, **_kwargs):
            raise AssertionError("SQL command should be blocked before connecting")

        self.runner.run_mysql = fail_connect
        code, _stdout, stderr = self.run_main(
            "sql",
            "--source",
            "order-mysql",
            "--sql",
            "delete from refunds where id = 1",
        )

        self.assertEqual(code, 2)
        self.assertIn("not read-only", stderr)

    def test_read_only_sql_still_executes_normally(self) -> None:
        calls = []

        def fake_run_mysql(source, sql, max_rows):
            calls.append((source, sql, max_rows))
            return {"source": source["name"], "type": "mysql", "row_count": 0, "rows": []}

        self.runner.run_mysql = fake_run_mysql
        code, stdout, stderr = self.run_main(
            "sql",
            "--source",
            "order-mysql",
            "--sql",
            "select * from refunds limit 1",
        )

        self.assertEqual(code, 0, stderr)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "select * from refunds limit 1")
        self.assertFalse(json.loads(stdout).get("dry_run", False))

    def test_sql_dry_run_with_allow_write_previews_without_connecting(self) -> None:
        def fail_connect(*_args, **_kwargs):
            raise AssertionError("dry-run must not connect")

        self.runner.run_mysql = fail_connect
        code, stdout, stderr = self.run_main(
            "sql",
            "--source",
            "order-mysql",
            "--sql",
            "update refunds set status = 'reviewed' where id = 1",
            "--allow-write",
            "--dry-run",
        )

        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["operation"], "sql")
        self.assertEqual(payload["source"]["name"], "order-mysql")
        self.assertEqual(payload["source"]["password"], "***")
        self.assertTrue(payload["safety"]["allow_write"])
        self.assertTrue(payload["safety"]["requires_confirmation"])
        self.assertEqual(payload["preview"]["sql"], "update refunds set status = 'reviewed' where id = 1")

    def test_es_dry_run_with_allow_write_previews_without_requesting(self) -> None:
        code, stdout, stderr = self.run_main(
            "es",
            "--source",
            "logs-es",
            "--method",
            "DELETE",
            "--path",
            "/old-index",
            "--allow-write",
            "--dry-run",
        )

        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["operation"], "elasticsearch")
        self.assertEqual(payload["preview"]["method"], "DELETE")
        self.assertEqual(payload["preview"]["path"], "/old-index")
        self.assertEqual(payload["source"]["url"], "https://***:***@example.internal:9200")
        self.assertTrue(payload["safety"]["requires_confirmation"])

    def test_cypher_dry_run_with_allow_write_previews_without_connecting(self) -> None:
        code, stdout, stderr = self.run_main(
            "cypher",
            "--source",
            "graph-neo4j",
            "--cypher",
            "MATCH (n:Temp) DELETE n",
            "--allow-write",
            "--dry-run",
        )

        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["operation"], "cypher")
        self.assertEqual(payload["source"]["uri"], "bolt://neo4j.example.internal:7687")
        self.assertEqual(payload["source"]["password"], "***")
        self.assertEqual(payload["preview"]["cypher"], "MATCH (n:Temp) DELETE n")
        self.assertTrue(payload["safety"]["requires_confirmation"])


if __name__ == "__main__":
    unittest.main()
