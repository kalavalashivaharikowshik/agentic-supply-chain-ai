"""Tests for the individual agents and the orchestrated cycle."""

from agents.budget_agent import BudgetAgent
from agents.inventory_agent import InventoryAgent
from agents.procurement_agent import ProcurementAgent
from agents.risk_agent import RiskAgent
from orchestrator.agent_graph import HAS_LANGGRAPH, _run_sequential, run_agent_cycle


def test_risk_agent_returns_active_risks_sorted(db):
    risks = RiskAgent().check_risks()
    assert [r["severity_score"] for r in risks] == sorted((r["severity_score"] for r in risks), reverse=True)
    assert risks[0]["risk_level"] == "HIGH"
    RiskAgent().resolve_risk(risks[0]["event_id"])
    assert len(RiskAgent().check_risks()) == len(risks) - 1


def test_inventory_agent_flags_low_cover():
    items = {i["product_name"]: i for i in InventoryAgent().check_inventory()}
    assert items["Semiconductor"]["days_of_cover"] == 4.5
    assert items["Semiconductor"]["status"] == "CRITICAL"
    assert items["OLED Display"]["status"] == "LOW"
    assert items["Chassis Frame"]["status"] == "OK"
    assert items["Semiconductor"]["in_transit"] == 2300


def test_procurement_agent_avoids_high_risk_locations():
    risks = RiskAgent().check_risks()  # Shanghai Port HIGH -> China is risky
    ranked = ProcurementAgent().rank("Semiconductor", risks)
    china = [s for s in ranked if s["country"] == "China"][0]
    assert china["at_risk_location"]
    assert ranked[-1]["country"] == "China"


def test_procurement_plan_covers_target():
    item = [i for i in InventoryAgent().check_inventory() if i["product_name"] == "Semiconductor"][0]
    plan = ProcurementAgent().plan_order(item)
    assert plan["supplier_name"] == "ABC Microchips"
    assert plan["quantity"] % 50 == 0 and plan["quantity"] > 0
    assert plan["total_cost"] == round(plan["quantity"] * plan["unit_price"], 2)
    assert "Reasons" in plan["explanation"]


def test_budget_agent_limits():
    agent = BudgetAgent()
    remaining = agent.remaining_budget()
    assert remaining == 100000 - 44200  # only this month's approved seed order counts
    assert agent.approve_budget(1000)
    assert not agent.approve_budget(remaining + 1)
    assert not agent.evaluate(agent.max_single_order + 1, remaining=10**9)["approved"]


def test_full_cycle_creates_orders_and_is_idempotent(db):
    state = run_agent_cycle(auto_execute=True)
    actions = {d["product_name"]: d["action"] for d in state["decisions"]}
    assert actions == {"Semiconductor": "ESCALATE", "OLED Display": "APPROVE"}
    assert len(state["orders"]) == 2
    statuses = {o["status"] for o in state["orders"]}
    assert statuses == {"Approved", "Pending Approval"}

    # orders are now on order -> a second cycle must not duplicate them
    again = run_agent_cycle(auto_execute=True)
    assert again["orders"] == []
    assert db.fetch_one("SELECT COUNT(*) AS n FROM agent_decisions WHERE agent_name = 'Orchestrator'")["n"] == 2


def test_dry_run_creates_no_orders(db):
    before = db.fetch_one("SELECT COUNT(*) AS n FROM purchase_orders")["n"]
    state = run_agent_cycle(auto_execute=False)
    assert state["decisions"]
    assert db.fetch_one("SELECT COUNT(*) AS n FROM purchase_orders")["n"] == before


def test_sequential_fallback_matches_graph():
    state = _run_sequential({"auto_execute": False})
    assert "summary" in state and len(state["decisions"]) == 2
    if HAS_LANGGRAPH:
        graph_state = run_agent_cycle(auto_execute=False)
        assert [d["action"] for d in graph_state["decisions"]] == [d["action"] for d in state["decisions"]]
