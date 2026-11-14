from database.data_loader import DataLoader
from database.mysql_connector import MySQLConnector


def test_auto_initializes_and_seeds(db):
    assert db.backend == "sqlite"
    assert db.is_connected
    assert db.fetch_one("SELECT COUNT(*) AS n FROM suppliers")["n"] == 11
    assert db.fetch_one("SELECT COUNT(*) AS n FROM products")["n"] == 4


def test_connect_and_close_are_idempotent():
    db = MySQLConnector(auto_connect=False)
    assert not db.is_connected
    db.connect()
    db.connect()
    assert db.is_connected
    db.close()
    db.close()
    assert not db.is_connected
    assert db.fetch_all("SELECT 1") == []  # safe when disconnected


def test_parameterized_queries_and_insert_returns_id(db):
    new_id = db.execute_query(
        "INSERT INTO agent_decisions (agent_name, decision_type, decision_description) VALUES (%s,%s,%s)",
        ("Test Agent", "Test", "hello"),
    )
    assert isinstance(new_id, int)
    row = db.fetch_one("SELECT * FROM agent_decisions WHERE decision_id = %s", (new_id,))
    assert row["agent_name"] == "Test Agent"


def test_reset_restores_seed(db):
    db.execute_query("DELETE FROM agent_decisions")
    DataLoader(db).reset()
    assert db.fetch_one("SELECT COUNT(*) AS n FROM agent_decisions")["n"] == 2
