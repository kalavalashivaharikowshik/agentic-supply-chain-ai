-- SQLite version of database/schema.sql.
-- Used automatically when no MySQL connection is configured, so the project
-- runs out of the box for demos and tests. Keep in sync with schema.sql.

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name      TEXT    NOT NULL,
    country            TEXT    NOT NULL,
    product_category   TEXT    NOT NULL,
    reliability_score  REAL    NOT NULL,
    price_index        REAL    NOT NULL,
    average_lead_time  INTEGER NOT NULL,
    capacity_per_month INTEGER NOT NULL DEFAULT 10000,
    is_active          INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS products (
    product_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name   TEXT    NOT NULL,
    category       TEXT    NOT NULL,
    unit_price     REAL    NOT NULL,
    daily_usage    INTEGER NOT NULL,
    reorder_point  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id          INTEGER NOT NULL REFERENCES products(product_id),
    warehouse_location  TEXT    NOT NULL,
    stock_quantity      INTEGER NOT NULL,
    last_updated        TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    vessel_name       TEXT    NOT NULL,
    supplier_id       INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    product_id        INTEGER NOT NULL REFERENCES products(product_id),
    quantity          INTEGER NOT NULL,
    origin_port       TEXT    NOT NULL,
    destination_port  TEXT    NOT NULL,
    status            TEXT    NOT NULL DEFAULT 'In Transit',
    progress          REAL    NOT NULL DEFAULT 0,
    delay_days        INTEGER NOT NULL DEFAULT 0,
    eta               TEXT
);

CREATE TABLE IF NOT EXISTS risk_events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT    NOT NULL,
    location        TEXT    NOT NULL,
    severity_score  INTEGER NOT NULL,
    risk_level      TEXT    NOT NULL DEFAULT 'LOW',
    description     TEXT,
    detected_by     TEXT    NOT NULL DEFAULT 'System',
    status          TEXT    NOT NULL DEFAULT 'Active',
    detected_at     TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id   INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL,
    total_price   REAL    NOT NULL,
    order_status  TEXT    NOT NULL DEFAULT 'Pending Approval',
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_decisions (
    decision_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name            TEXT NOT NULL,
    decision_type         TEXT NOT NULL,
    decision_description  TEXT NOT NULL,
    created_at            TEXT DEFAULT CURRENT_TIMESTAMP
);
