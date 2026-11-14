"""Application settings.

Business rules come from ``config.yaml``; connection details and secrets come
from environment variables (optionally loaded from a ``.env`` file).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent

try:  # optional: load .env if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:  # pragma: no cover
    pass


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


@dataclass
class Settings:
    config: Dict[str, Any] = field(default_factory=dict)

    # ---- database ----
    @property
    def use_mysql(self) -> bool:
        return _env("MYSQLHOST") is not None

    @property
    def mysql(self) -> Dict[str, Any]:
        return {
            "host": _env("MYSQLHOST"),
            "user": _env("MYSQLUSER", "root"),
            "password": _env("MYSQLPASSWORD", ""),
            "database": _env("MYSQLDATABASE", "supply_chain"),
            "port": int(_env("MYSQLPORT", "3306")),
            "ssl_disabled": _env("MYSQL_SSL_DISABLED", "true").lower() == "true",
        }

    @property
    def sqlite_path(self) -> str:
        return _env("SQLITE_PATH", str(PROJECT_ROOT / "data" / "supply_chain.db"))

    # ---- neo4j (optional) ----
    @property
    def neo4j_uri(self) -> Optional[str]:
        return _env("NEO4J_URI")

    @property
    def neo4j_user(self) -> str:
        return _env("NEO4J_USER", "neo4j")

    @property
    def neo4j_password(self) -> Optional[str]:
        return _env("NEO4J_PASSWORD")

    # ---- external APIs ----
    @property
    def news_api_key(self) -> Optional[str]:
        return _env("NEWS_API_KEY")

    @property
    def enable_external_apis(self) -> bool:
        return _env("ENABLE_EXTERNAL_APIS", "true").lower() == "true"

    # ---- business rules ----
    def get(self, dotted_key: str, default: Any = None) -> Any:
        node: Any = self.config
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    @property
    def ports(self) -> List[Dict[str, Any]]:
        return self.get("ports", []) or []


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    config_path = Path(_env("CONFIG_PATH", str(PROJECT_ROOT / "config.yaml")))
    config: Dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh) or {}
    return Settings(config=config)
