#!/usr/bin/env python3
"""Check local prerequisites for the agent-datasource skill."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path


DRIVERS = {
    "yaml": "PyYAML",
    "pymysql": "PyMySQL",
    "psycopg": "psycopg[binary]",
    "requests": "requests",
    "neo4j": "neo4j",
}


def config_candidates() -> list[Path]:
    configured = os.environ.get("AGENT_DATASOURCE_CONFIG")
    if configured:
        return [Path(configured).expanduser()]
    root = Path.home() / ".config" / "agent-datasource"
    return [root / "config.yaml", root / "config.yml"]


def main() -> int:
    modules = {
        module: importlib.util.find_spec(module) is not None
        for module in DRIVERS
    }
    candidates = config_candidates()
    found_config = next((path for path in candidates if path.exists()), None)
    result = {
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
            "ok": sys.version_info >= (3, 10),
        },
        "uv": {
            "path": shutil.which("uv"),
            "ok": shutil.which("uv") is not None,
        },
        "config": {
            "env": os.environ.get("AGENT_DATASOURCE_CONFIG"),
            "candidates": [str(path) for path in candidates],
            "found": str(found_config) if found_config else None,
            "ok": found_config is not None,
        },
        "drivers": {
            module: {"package": package, "ok": ok}
            for module, package in DRIVERS.items()
            for ok in [modules[module]]
        },
    }
    result["ok"] = (
        result["python"]["ok"]
        and result["uv"]["ok"]
        and result["config"]["ok"]
        and all(item["ok"] for item in result["drivers"].values())
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        print()
        print("Preferred run mode:")
        print("  uv run scripts/agent_datasource.py check-env")
        print()
        print("Manual package installation when uv is unavailable:")
        print(
            '  python3 -m pip install "psycopg[binary]>=3.2,<4" '
            '"PyMySQL>=1.1,<2" "requests>=2.32,<3" "neo4j>=5,<7" "PyYAML>=6,<7"'
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
