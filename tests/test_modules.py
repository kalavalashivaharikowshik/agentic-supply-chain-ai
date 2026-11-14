"""Unit tests for the analytical building blocks."""

import pytest

from analytics.kpi_monitor import KPIMonitor
from conflict_resolver.decision_maker import DecisionMaker
from conflict_resolver.rule_engine import RuleEngine
from digital_twin.impact_analyzer import ImpactAnalyzer
from digital_twin.simulation_engine import SimulationEngine
from explainability.decision_explainer import DecisionExplainer
from forecasting.demand_forecast import DemandForecast
from forecasting.inventory_forecast import InventoryForecast
from logistics.port_monitor import PortMonitor
from logistics.route_optimizer import RouteOptimizer
from logistics.shipment_tracker import ShipmentTracker, interpolate_position
from procurement.cost_optimizer import CostOptimizer
from procurement.purchase_order_generator import PurchaseOrderGenerator
from procurement.supplier_ranking import SupplierRanking
from risk_analysis.news_sentiment import NewsSentiment
from risk_analysis.risk_scorer import RiskScorer
from risk_analysis.weather_monitor import WeatherMonitor


# ---------------------------------------------------------------- risk
@pytest.mark.parametrize("score,level", [(0, "LOW"), (20, "MEDIUM"), (50, "HIGH"), (79, "HIGH"), (80, "CRITICAL")])
def test_risk_scorer_levels(score, level):
    assert RiskScorer().calculate_risk(score) == level


def test_wind_score_is_bounded():
    s = RiskScorer()
    assert s.score_wind(0) == 0
    assert s.score_wind(45) == 50
    assert s.score_wind(500) == 100


def test_weather_monitor_with_fake_api():
    class FakeAPI:
        def get_weather(self, lat, lon):
            return {"windspeed": 81, "weathercode": 95, "temperature": 24}

    event = WeatherMonitor(api=FakeAPI()).check_weather_risk(1, 2, "Test Port")
    assert event["risk_level"] == "CRITICAL" and event["location"] == "Test Port"
    assert len(WeatherMonitor(api=FakeAPI()).check_all_ports()) == 8


def test_weather_monitor_handles_api_outage():
    class DownAPI:
        def get_weather(self, lat, lon):
            return None

    assert WeatherMonitor(api=DownAPI()).check_weather_risk(1, 2) is None


def test_news_sentiment_scores_and_locates():
    ns = NewsSentiment()
    risks = ns.analyze_articles([
        {"title": "Dock workers strike shuts Rotterdam port", "description": ""},
        {"title": "Quarterly earnings beat expectations", "description": ""},
    ])
    assert len(risks) == 1
    assert risks[0]["location"] == "Rotterdam Port"
    assert risks[0]["severity_score"] >= 30


# ---------------------------------------------------------------- procurement
def test_supplier_ranking_prefers_reliable_cheap_fast():
    suppliers = [
        {"supplier_id": 1, "supplier_name": "A", "reliability_score": 0.99, "price_index": 10, "average_lead_time": 5},
        {"supplier_id": 2, "supplier_name": "B", "reliability_score": 0.70, "price_index": 20, "average_lead_time": 20},
        {"supplier_id": 3, "supplier_name": "C", "reliability_score": 0.85, "price_index": 15, "average_lead_time": 10},
    ]
    ranked = SupplierRanking().rank_suppliers(suppliers)
    assert [s["supplier_name"] for s in ranked] == ["A", "C", "B"]
    assert ranked[0]["score"] == 100.0
    assert SupplierRanking().rank_suppliers([]) == []


def test_order_quantity():
    opt = CostOptimizer()
    # 100/day * (30 target + 10 lead) - 1000 stock - 500 transit = 2500
    assert opt.order_quantity(1000, 100, in_transit=500, lead_time_days=10) == 2500
    assert opt.order_quantity(10**6, 100) == 0
    assert opt.order_quantity(0, 100, capacity=1000) == 1000
    assert opt.calculate_cost(2.5, 4) == 10.0


def test_purchase_order_validation(db):
    gen = PurchaseOrderGenerator()
    order_id = gen.create_order(1, 1, 100, 4150.0)
    gen.update_status(order_id, "Approved")
    assert db.fetch_one("SELECT order_status FROM purchase_orders WHERE order_id = %s", (order_id,))["order_status"] == "Approved"
    with pytest.raises(ValueError):
        gen.create_order(1, 1, 0, 0)
    with pytest.raises(ValueError):
        gen.update_status(order_id, "Lost")


def test_explainer_uses_real_numbers():
    best = {"supplier_name": "A", "country": "X", "reliability_score": 0.95, "price_index": 10, "average_lead_time": 5, "score": 90}
    alt = {"supplier_name": "B", "country": "Y", "reliability_score": 0.85, "price_index": 12, "average_lead_time": 9}
    text = DecisionExplainer().explain_supplier_choice(best, [alt])
    assert "+10.0 pts" in text and "-16.7%" in text and "-4.0 days" in text


# ---------------------------------------------------------------- conflict resolution
@pytest.mark.parametrize("stock_days,cost,risk,expected", [
    (3, 50000, "HIGH", "URGENT_PROCUREMENT"),
    (3, 150000, "LOW", "ESCALATE"),
    (20, 150000, "LOW", "REJECT_COST"),
    (20, 1000, "CRITICAL", "RISK_MITIGATION"),
    (20, 1000, "LOW", "NORMAL_OPERATION"),
])
def test_rule_engine(stock_days, cost, risk, expected):
    assert RuleEngine().evaluate(stock_days, cost, risk) == expected
    assert DecisionMaker().make_decision(stock_days, cost, risk) == expected


# ---------------------------------------------------------------- forecasting
def test_linear_forecast_follows_trend():
    assert DemandForecast().forecast_demand([1, 2, 3], periods=3) == [4.0, 5.0, 6.0]
    assert DemandForecast.linear_forecast([], 2) == [0.0, 0.0]
    assert DemandForecast.linear_forecast([7], 2) == [7.0, 7.0]


def test_inventory_forecast():
    f = InventoryForecast()
    assert f.predict_stockout(1000, 100) == 10
    assert f.predict_stockout(1000, 0) is None
    assert f.predict_stockout_from_forecast(250, [100, 100, 100]) == 3
    assert f.predict_stockout_from_forecast(1000, [100, 100]) is None


# ---------------------------------------------------------------- digital twin
def test_impact_analyzer():
    a = ImpactAnalyzer()
    assert a.analyze_delay(1000, 100, 12, unit_price=5)["status"] == "Production Risk"
    r = a.analyze_delay(1000, 100, 12, unit_price=5)
    assert r["shortfall_units"] == 200 and r["revenue_at_risk"] == 1000
    assert a.analyze_delay(1000, 100, 8)["status"] == "At Risk"
    assert a.analyze_delay(1000, 100, 2)["status"] == "No Risk"


def test_simulations_use_live_inventory():
    engine = SimulationEngine()
    delay = engine.run_delay_simulation(10)
    assert delay["overall_status"] == "Production Risk"
    at_risk = {i["product_name"] for i in delay["impacts"] if i["status"] == "Production Risk"}
    assert at_risk == {"Semiconductor", "OLED Display"}

    failure = engine.simulate_supplier_failure(10, 30)  # chassis supplier
    assert [i["product_name"] for i in failure["impacts"]] == ["Chassis Frame"]

    closure = engine.simulate_port_closure("Shanghai Port", 60)
    assert [i["product_name"] for i in closure["impacts"]] == ["Battery Pack"]

    with pytest.raises(ValueError):
        engine.simulate_supplier_failure(999)


# ---------------------------------------------------------------- logistics
def test_route_optimizer():
    r = RouteOptimizer()
    assert r.recommend(100, deadline_days=30)["mode"] == "Sea Freight"
    assert r.recommend(100, deadline_days=10)["mode"] == "Air Freight"
    assert r.recommend(100, deadline_days=1)["mode"] == "Air Freight"  # nothing meets deadline -> fastest
    assert r.choose_route(cost=100000, time=2) == "Air Freight"


def test_interpolate_position_wraps_dateline():
    lat, lon = interpolate_position("Busan Port", "Los Angeles Port", 0.5)
    assert lon > 150 or lon < -150  # crosses the Pacific, not Europe
    assert interpolate_position("Busan Port", "Los Angeles Port", 0) == pytest.approx((35.10, 129.04))


def test_shipment_tracking_and_delivery(db):
    tracker = ShipmentTracker()
    statuses = {s["vessel_name"]: s for s in tracker.check_shipments()}
    assert statuses["Maersk Horizon"]["delay_risk"] >= 50
    before = db.fetch_one("SELECT stock_quantity FROM inventory WHERE product_id = 1")["stock_quantity"]
    delivered = tracker.advance_shipments(step=1.0)
    assert delivered >= 1
    after = db.fetch_one("SELECT stock_quantity FROM inventory WHERE product_id = 1")["stock_quantity"]
    assert after == before + 1500 + 800  # both semiconductor shipments arrived


def test_port_monitor():
    status = PortMonitor().check_port_status("Chennai Port")
    assert status["inbound_shipments"] == 2
    assert status["status"] in {"NORMAL", "MEDIUM CONGESTION", "HIGH CONGESTION"}


# ---------------------------------------------------------------- KPIs
def test_kpis_from_live_data():
    k = KPIMonitor().compute_all()
    assert k["active_risks"] == 2
    assert k["stock_alerts"] == 2
    assert k["delayed_shipments"] == 2
    assert k["budget_used_pct"] == 44.2
    assert 0 <= k["resilience_score"] <= 100
    assert KPIMonitor().shipping_delay_avg([]) == 0.0
