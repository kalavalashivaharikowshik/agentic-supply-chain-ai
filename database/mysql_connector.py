"""Database access layer.

Uses MySQL when ``MYSQLHOST`` is set in the environment, otherwise falls back
to a local SQLite file so the project runs with zero setup. Both backends
expose the same API and accept ``%s`` style query parameters.

Usage::

    with MySQLConnector() as db:
        rows = db.fetch_all("SELECT * FROM suppliers WHERE country = %s", ("India",))
"""

from __future__ import annotations

import os
import sqlite3
import threading
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence

from app.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

_init_lock = threading.Lock()
_initialized_targets: set = set()


def _normalize(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert DB-specific types (e.g. MySQL Decimal) into plain Python types."""
    return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in row.items()}


class MySQLConnector:
    """Thin wrapper around MySQL / SQLite with a uniform interface."""

    def __init__(self, auto_connect: bool = True, auto_init: bool = True):
        self.settings = get_settings()
        self.backend = "mysql" if self.settings.use_mysql else "sqlite"
        self.connection = None
        self._auto_init = auto_init
        if auto_connect:
            self.connect()

    # ------------------------------------------------------------------ #
    # connection management
    # ------------------------------------------------------------------ #
    def connect(self):
        """Open the connection (safe to call more than once)."""
        if self.connection is not None:
            return self.connection
        try:
            if self.backend == "mysql":
                import mysql.connector

                cfg = self.settings.mysql
                self.connection = mysql.connector.connect(
                    host=cfg["host"],
                    user=cfg["user"],
                    password=cfg["password"],
                    database=cfg["database"],
                    port=cfg["port"],
                    ssl_disabled=cfg["ssl_disabled"],
                    autocommit=False,
                )
            else:
                path = self.settings.sqlite_path
                if path != ":memory:":
                    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                self.connection = sqlite3.connect(path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self.connection.execute("PRAGMA foreign_keys = ON")
        except Exception as exc:  # pragma: no cover - depends on infra
            logger.error("Database connection failed (%s): %s", self.backend, exc)
            self.connection = None
            return None

        if self._auto_init:
            self._ensure_initialized()
        return self.connection

    def close(self) -> None:
        if self.connection is not None:
            try:
                self.connection.close()
            finally:
                self.connection = None

    @property
    def is_connected(self) -> bool:
        return self.connection is not None

    def __enter__(self) -> "MySQLConnector":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------------ #
    # queries
    # ------------------------------------------------------------------ #
    def _prepare(self, query: str) -> str:
        return query.replace("%s", "?") if self.backend == "sqlite" else query

    def _cursor(self):
        if self.backend == "mysql":
            return self.connection.cursor(dictionary=True)
        return self.connection.cursor()

    def fetch_all(self, query: str, params: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
        """Run a SELECT and return a list of dict rows ([] if not connected)."""
        if self.connection is None:
            return []
        cursor = self._cursor()
        try:
            cursor.execute(self._prepare(query), tuple(params or ()))
            rows = cursor.fetchall()
            return [_normalize(dict(r)) for r in rows]
        finally:
            cursor.close()

    def fetch_one(self, query: str, params: Optional[Sequence[Any]] = None) -> Optional[Dict[str, Any]]:
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def execute_query(self, query: str, params: Optional[Sequence[Any]] = None) -> Optional[int]:
        """Run INSERT/UPDATE/DELETE, commit, and return the last inserted id."""
        if self.connection is None:
            logger.warning("execute_query skipped: no database connection")
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute(self._prepare(query), tuple(params or ()))
            self.connection.commit()
            return cursor.lastrowid
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def execute_script(self, sql: str) -> None:
        """Execute a multi-statement SQL script."""
        if self.connection is None:
            return
        if self.backend == "sqlite":
            self.connection.executescript(sql)
            self.connection.commit()
            return
        cursor = self.connection.cursor()
        try:
            for statement in _split_sql(sql):
                cursor.execute(statement)
            self.connection.commit()
        finally:
            cursor.close()

    # ------------------------------------------------------------------ #
    def _ensure_initialized(self) -> None:
        target = self.settings.sqlite_path if self.backend == "sqlite" else self.settings.mysql["host"]
        if target in _initialized_targets and target != ":memory:":
            return
        with _init_lock:
            if target in _initialized_targets and target != ":memory:":
                return
            from database.data_loader import DataLoader

            DataLoader(self).initialize()
            _initialized_targets.add(target)


def _split_sql(sql: str) -> List[str]:
    """Split a SQL script on ``;`` while respecting quoted strings and ``--`` comments."""
    statements, buf, quote = [], [], None
    i = 0
    while i < len(sql):
        ch = sql[i]
        if quote:
            buf.append(ch)
            if ch == quote:
                if i + 1 < len(sql) and sql[i + 1] == quote:  # escaped '' inside string
                    buf.append(sql[i + 1])
                    i += 1
                else:
                    quote = None
        elif ch in ("'", '"', "`"):
            quote = ch
            buf.append(ch)
        elif ch == "-" and sql.startswith("--", i):
            newline = sql.find("\n", i)
            i = len(sql) if newline == -1 else newline
            continue
        elif ch == ";":
            stmt = "".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def reset_initialization_cache() -> None:
    """Used by tests that point the app at a fresh database."""
    _initialized_targets.clear()


# Friendlier alias
Database = MySQLConnector
