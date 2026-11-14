"""CLI, query engine, recovery loop and dashboard smoke tests."""

import pytest

from app.main import main
from autonomous.recovery_loop import RecoveryLoop
from query_engine import QueryEngine


@pytest.mark.parametrize("question,expected", [
    ("Which suppliers provide semiconductors?", "ABC Microchips"),
    ("who supplies batteries", "Nordic Cell Systems"),
    ("what is low on stock?", "Semiconductor"),
    ("show active risks", "Shanghai Port"),
    ("any delayed shipments?", "Maersk Horizon"),
    ("show purchase orders", "PO #1"),
    ("how healthy is the supply chain", "Resilience score"),
    ("asdfgh", "couldn't understand"),
])
def test_query_engine(question, expected):
    assert expected in QueryEngine().ask(question)


def test_recovery_loop_triggers_agents_on_production_risk():
    result = RecoveryLoop(scan_external=False).run(delay_days=10)
    assert result["simulation"]["overall_status"] == "Production Risk"
    assert result["cycle"] is not None and result["cycle"]["orders"]


def test_recovery_loop_no_action_for_short_delay():
    result = RecoveryLoop(scan_external=False).run(delay_days=1)
    assert result["cycle"] is None


def test_cli_commands(capsys):
    main(["init-db"])
    main(["run-agents", "--dry-run"])
    main(["ask", "show", "risks"])
    main(["simulate", "--delay", "5"])
    main(["forecast", "1", "2", "3", "--periods", "2"])
    main(["kpis"])
    out = capsys.readouterr().out
    assert "Database ready" in out and "Inventory alerts" in out and "[4.0, 5.0]" in out


def test_dashboard_renders_without_errors():
    st_testing = pytest.importorskip("streamlit.testing.v1")
    pytest.importorskip("streamlit_folium")
    at = st_testing.AppTest.from_file("../control_tower/dashboard.py", default_timeout=60).run()
    assert not at.exception
    assert len(at.metric) == 8
    labels = [b.label for b in at.sidebar.button]
    at.sidebar.button[labels.index("🧠 Run Agent Cycle")].click().run()
    assert not at.exception
    assert any("Last agent cycle" in i.value for i in at.info)
