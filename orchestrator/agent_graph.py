"""Multi-agent orchestration with LangGraph.

Flow::

    risk ──► inventory ──┬─(alerts)──► procurement ──► budget ──► execute ──► report ──► END
                         └─(no alerts)──────────────────────────────────────► report

* **Risk Agent** loads active disruptions (optionally scanning weather/news).
* **Inventory Agent** computes days of cover and raises alerts.
* **Procurement Agent** picks a supplier for each alert, avoiding high-risk locations.
* **Budget Agent + Rule Engine** resolve conflicts between urgency, cost and risk.
* **Execute** creates purchase orders (approved or pending human approval).

If LangGraph is not installed the same nodes run sequentially.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from agents.budget_agent import BudgetAgent
from agents.inventory_agent import InventoryAgent
from agents.procurement_agent import ProcurementAgent
from agents.risk_agent import RiskAgent
from conflict_resolver.rule_engine import RuleEngine
from procurement.purchase_order_generator import PurchaseOrderGenerator
from utils.helpers import log_decision
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    from langgraph.graph import END, StateGraph

    HAS_LANGGRAPH = True
except Exception:  # pragma: no cover
    HAS_LANGGRAPH = False
    END = "__end__"


class AgentState(TypedDict, total=False):
    scan_external: bool
    auto_execute: bool
    risks: List[Dict[str, Any]]
    max_risk_level: str
    inventory: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    plans: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    orders: List[Dict[str, Any]]
    supplier: Optional[Dict[str, Any]]
    approved: bool
    summary: str


LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


# ---------------------------------------------------------------------- nodes
def risk_node(state: AgentState) -> AgentState:
    risks = RiskAgent().check_risks(scan_external=state.get("scan_external", False))
    max_level = max((r["risk_level"] for r in risks), key=LEVELS.index, default="LOW")
    return {"risks": risks, "max_risk_level": max_level}


def inventory_node(state: AgentState) -> AgentState:
    items = InventoryAgent().check_inventory()
    return {"inventory": items, "alerts": [i for i in items if i["status"] != "OK"]}


def route_after_inventory(state: AgentState) -> str:
    return "procurement" if state.get("alerts") else "report"


def procurement_node(state: AgentState) -> AgentState:
    agent = ProcurementAgent()
    plans = []
    for alert in state.get("alerts", []):
        plan = agent.plan_order(alert, state.get("risks"))
        if plan:
            plans.append(plan)
    # most urgent first so they get budget priority
    plans.sort(key=lambda p: (p["days_of_cover"] is None, p["days_of_cover"] or 0))
    return {"plans": plans, "supplier": plans[0]["supplier"] if plans else None}


def budget_node(state: AgentState) -> AgentState:
    budget = BudgetAgent()
    engine = RuleEngine()
    remaining = budget.remaining_budget()
    decisions = []
    for plan in state.get("plans", []):
        check = budget.evaluate(plan["total_cost"], remaining)
        rule = engine.evaluate_detailed(plan["days_of_cover"], plan["total_cost"],
                                        state.get("max_risk_level", "LOW"), remaining)
        if check["approved"]:
            action = "APPROVE"
            remaining -= plan["total_cost"]
        elif rule["decision"] == "ESCALATE" or plan["stock_status"] == "CRITICAL":
            action = "ESCALATE"  # urgent but over limit -> human approval
        else:
            action = "REJECT"
        decisions.append({**plan, "action": action, "rule_decision": rule["decision"],
                          "budget_reason": check["reason"], "rule_reasons": rule["reasons"]})
    return {"decisions": decisions, "approved": any(d["action"] == "APPROVE" for d in decisions)}


def execute_node(state: AgentState) -> AgentState:
    orders = []
    generator = PurchaseOrderGenerator()
    for d in state.get("decisions", []):
        msg = (f"{d['action']}: {d['quantity']} x {d['product_name']} from {d['supplier_name']} "
               f"for {d['total_cost']:,.2f} ({d['budget_reason']}; rule {d['rule_decision']})")
        if state.get("auto_execute", True) and d["action"] in ("APPROVE", "ESCALATE"):
            status = "Approved" if d["action"] == "APPROVE" else "Pending Approval"
            order_id = generator.create_order(d["supplier_id"], d["product_id"], d["quantity"], d["total_cost"], status)
            orders.append({"order_id": order_id, "status": status, **{k: d[k] for k in
                           ("product_name", "supplier_name", "quantity", "total_cost")}})
            msg += f" → PO #{order_id} ({status})"
        log_decision("Procurement Agent" if d["action"] == "APPROVE" else "Budget Agent", "Purchase Decision", msg)
    return {"orders": orders}


def report_node(state: AgentState) -> AgentState:
    risks = state.get("risks", [])
    alerts = state.get("alerts", [])
    decisions = state.get("decisions", [])
    orders = state.get("orders", [])
    lines = [
        f"Active risks: {len(risks)} (max level {state.get('max_risk_level', 'LOW')})",
        f"Inventory alerts: {len(alerts)}" + (
            " – " + ", ".join(f"{a['product_name']} {a['days_of_cover']}d" for a in alerts) if alerts else ""),
    ]
    for d in decisions:
        lines.append(f"{d['action']}: {d['quantity']} x {d['product_name']} from {d['supplier_name']} "
                     f"({d['total_cost']:,.2f})")
    lines.append(f"Purchase orders created: {len(orders)}")
    summary = "\n".join(lines)
    log_decision("Orchestrator", "Cycle Summary", summary.replace("\n", " | "))
    return {"summary": summary}


# ---------------------------------------------------------------------- graph
def build_graph():
    if not HAS_LANGGRAPH:
        raise RuntimeError("langgraph is not installed")
    graph = StateGraph(AgentState)
    graph.add_node("risk", risk_node)
    graph.add_node("inventory", inventory_node)
    graph.add_node("procurement", procurement_node)
    graph.add_node("budget", budget_node)
    graph.add_node("execute", execute_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("risk")
    graph.add_edge("risk", "inventory")
    graph.add_conditional_edges("inventory", route_after_inventory,
                                {"procurement": "procurement", "report": "report"})
    graph.add_edge("procurement", "budget")
    graph.add_edge("budget", "execute")
    graph.add_edge("execute", "report")
    graph.add_edge("report", END)
    return graph.compile()


def _run_sequential(state: AgentState) -> AgentState:
    for node in (risk_node, inventory_node):
        state.update(node(state))
    if route_after_inventory(state) == "procurement":
        for node in (procurement_node, budget_node, execute_node):
            state.update(node(state))
    state.update(report_node(state))
    return state


def run_agent_cycle(auto_execute: bool = True, scan_external: bool = False) -> AgentState:
    """Run one full decision cycle and return the final state."""
    initial: AgentState = {"auto_execute": auto_execute, "scan_external": scan_external}
    if HAS_LANGGRAPH:
        final = build_graph().invoke(initial)
    else:
        final = _run_sequential(dict(initial))
    logger.info("Agent cycle complete (%d order(s) created)", len(final.get("orders", [])))
    return final
