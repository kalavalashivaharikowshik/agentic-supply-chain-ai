from langgraph.graph import StateGraph
from agents.risk_agent import RiskAgent
from agents.inventory_agent import InventoryAgent
from agents.procurement_agent import ProcurementAgent
from agents.budget_agent import BudgetAgent


class AgentState(dict):
    pass


def risk_node(state):
    RiskAgent().check_risks()
    return state


def inventory_node(state):
    InventoryAgent().check_inventory()
    return state


def procurement_node(state):
    supplier = ProcurementAgent().find_best_supplier()
    state["supplier"] = supplier
    return state


def budget_node(state):
    if state.get("supplier"):
        cost = state["supplier"]["price_index"] * 100
        approved = BudgetAgent().approve_budget(cost)
        state["approved"] = approved
    return state


def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("risk", risk_node)
    graph.add_node("inventory", inventory_node)
    graph.add_node("procurement", procurement_node)
    graph.add_node("budget", budget_node)

    graph.set_entry_point("risk")

    graph.add_edge("risk", "inventory")
    graph.add_edge("inventory", "procurement")
    graph.add_edge("procurement", "budget")

    return graph.compile()