"""Shared fixtures: every test gets a fresh, seeded SQLite database and no network."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    from database.mysql_connector import reset_initialization_cache

    for var in ("MYSQLHOST", "NEO4J_URI", "NEO4J_PASSWORD", "NEWS_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("ENABLE_EXTERNAL_APIS", "false")
    reset_initialization_cache()
    yield tmp_path / "test.db"
    reset_initialization_cache()


@pytest.fixture
def db():
    from database.mysql_connector import MySQLConnector

    with MySQLConnector() as conn:
        yield conn
