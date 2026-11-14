# 🌍 Agentic AI Supply Chain Control Tower

A multi-agent system that monitors a global supply chain, detects disruptions,
simulates their impact with a digital twin, and **autonomously places
replenishment orders**, with each decision checked against budget and business
rules and explained in plain language.

![CI](https://github.com/kalavalashivaharikowshik/agentic-supply-chain-ai/actions/workflows/ci.yml/badge.svg)

---

## ✨ Features

| Area | What it does |
|---|---|
| 🤖 **Multi-agent orchestration** | A LangGraph state machine coordinates the Risk, Inventory, Procurement and Budget agents, with conditional routing |
| 🛰 **Risk detection** | Live weather for 8 major ports (Open-Meteo) and news headline scoring (NewsAPI) feed a 0–100 severity score |
| 📦 **Inventory intelligence** | Days of cover per product, counting stock in transit and on order; CRITICAL / LOW / OK classification |
| 🛒 **Risk-aware procurement** | Weighted supplier scoring (reliability, price, lead time). Suppliers in high-risk countries are avoided, and orders are sized to a target cover |
| 💰 **Budget & conflict resolution** | Monthly and per-order limits. Urgent orders over budget are **escalated for human approval** instead of being dropped |
| 🧪 **Digital twin** | What-if simulation of shipment delays, supplier failures and port closures, with shortfall units and revenue at risk |
| 🔁 **Autonomous recovery loop** | Detect → simulate → act, end to end |
| 🧠 **Explainability** | Every recommendation explains *why*, using the real numbers versus the alternatives |
| 💬 **Natural-language assistant** | Ask "what is low on stock?" or "who supplies batteries?" and get answers from live data |
| 🗺 **Control tower UI** | Streamlit dashboard with a live vessel map, risk zones, real KPIs, PO approvals and an agent activity log |
| 🕸 **Knowledge graph** | Optional Neo4j mirror of suppliers → products → countries → shipments (falls back to SQL) |

## 🏗 Architecture

```
                    ┌──────────────────── Streamlit Control Tower ───────────────────┐
                    │ map · KPIs · risks · agent log · procurement · twin · assistant │
                    └───────────────────────────────┬─────────────────────────────────┘
                                                    │
   Weather API ─┐                      ┌────────────▼────────────┐
   News API   ──┼─► Disruption ──────► │  LangGraph Orchestrator │ ◄── Recovery Loop
   Shipments  ──┘    Detector          │ risk → inventory ─┬─► procurement → budget → execute → report
                                       │                   └─(no alerts)────────────────────► report
                                       └────────────┬────────────┘
                                                    │
                     ┌──────────────┬───────────────┼───────────────┬──────────────┐
                Digital Twin   Rule Engine     Explainer      KPI Monitor    Query Engine
                                                    │
                                   MySQL / SQLite  ─┴─  Neo4j (optional)
```

### Project layout

```
agents/             Risk, Inventory, Procurement, Budget, Logistics agents
orchestrator/       LangGraph multi-agent workflow (agent_graph.py)
autonomous/         Detect → simulate → act recovery loop
risk_analysis/      Weather monitor, news sentiment, risk scorer, disruption detector
procurement/        Supplier discovery & ranking, order sizing, PO generator
logistics/          Shipment tracking/vessel movement, port congestion, route choice
digital_twin/       Disruption models, impact analyzer, simulation engine
forecasting/        Demand forecast (Prophet or linear trend), stockout prediction
conflict_resolver/  Business rules + rule engine
explainability/     Data-driven decision explanations
analytics/          Live KPI computation
query_engine/       Natural-language Q&A
knowledge_graph/    Neo4j connector, graph builder, queries (with SQL fallback)
api_connectors/     Weather, news, shipping, supplier data sources
control_tower/      Streamlit dashboard and panels
database/           Connector, schema (MySQL + SQLite), seed data, loader
app/                CLI entry point, settings, startup check
tests/              Pytest suite (54 tests)
```

## 🚀 Quick start (zero setup)

With no database configured, the app creates and seeds a local SQLite database automatically.

```bash
git clone https://github.com/kalavalashivaharikowshik/agentic-supply-chain-ai.git
cd agentic-supply-chain-ai
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run control_tower/dashboard.py
```

Open http://localhost:8501 and click **🧠 Run Agent Cycle** in the sidebar.

### With Docker (app + MySQL)

```bash
cp .env.example .env          # optional: add NEWS_API_KEY
docker compose up --build     # add "--profile graph" to also start Neo4j
```

### With your own MySQL (e.g. Railway)

```bash
cp .env.example .env
# set MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE
python -m app.main init-db    # creates tables + demo data (if empty)
python -m app.startup         # verify connection
```

## 🖥 CLI

```bash
python -m app.main init-db [--reset]                 # create / reset tables and demo data
python -m app.main run-agents [--dry-run] [--scan]   # one multi-agent decision cycle
python -m app.main recover [--delay 10] [--no-scan]  # autonomous recovery loop
python -m app.main detect-risks                      # scan weather + news
python -m app.main simulate --delay 12               # all supply delayed 12 days
python -m app.main simulate --supplier 1 --delay 20  # supplier failure
python -m app.main simulate --port "Busan Port" --delay 7
python -m app.main forecast 100 120 110 130 140 --periods 7
python -m app.main ask "Which suppliers provide semiconductors?"
python -m app.main kpis
python -m app.main sync-graph                        # mirror data into Neo4j
python -m app.main dashboard
```

Example output of `run-agents` on the demo data:

```
Active risks: 2 (max level HIGH)
Inventory alerts: 2 – Semiconductor 4.5d, OLED Display 8.0d
ESCALATE: 2200 x Semiconductor from ABC Microchips (91,300.00)
APPROVE: 700 x OLED Display from Osaka Display Corp (44,800.00)
Purchase orders created: 2
```

The semiconductor order is above the single-order limit, but stock is critical, so the
agents create it as **Pending Approval** for a human to approve in the dashboard. They skip
Shenzhen ChipTech because of the active HIGH risk at Shanghai Port.

## ⚙️ Configuration

* **`config.yaml`**: business rules (budget limits, stock-cover thresholds, risk thresholds,
  supplier-scoring weights, monitored ports).
* **`.env`**: connection details and secrets (see `.env.example`). Secrets are never stored in code.

| Variable | Purpose |
|---|---|
| `MYSQLHOST` … `MYSQLDATABASE` | Use MySQL. If `MYSQLHOST` is empty, SQLite is used |
| `SQLITE_PATH` | SQLite file location (default `data/supply_chain.db`) |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Optional knowledge graph |
| `NEWS_API_KEY` | Enables news-based risk detection |
| `ENABLE_EXTERNAL_APIS` | `false` disables all outbound calls (offline demos) |

## 🧪 Tests

```bash
pytest
```

Each test runs against its own fresh SQLite database with network calls disabled. CI also
runs the CLI against a real MySQL 8 service.

## 🗄 Data model

`suppliers`, `products`, `inventory`, `shipments`, `risk_events`, `purchase_orders`,
`agent_decisions` (audit log of every agent decision). See `database/schema.sql`.

## 📌 Notes

* Vessel positions are simulated along straight-line routes between ports.
  Plug a real AIS/carrier API into `api_connectors/shipping_api.py` for production.
* Demand forecasting uses Prophet when installed (`pip install prophet`), otherwise a linear trend.
