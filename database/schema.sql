-- SQL schema for the supply chain database (MySQL 8+)
-- Load with:  mysql -u <user> -p <database> < database/schema.sql
-- Then seed:  mysql -u <user> -p <database> < database/seed.sql

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id        INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name      VARCHAR(120) NOT NULL,
    country            VARCHAR(80)  NOT NULL,
    product_category   VARCHAR(80)  NOT NULL,
    reliability_score  DECIMAL(4,3) NOT NULL,          -- 0.000 - 1.000
    price_index        DECIMAL(8,2) NOT NULL,          -- unit price offered
    average_lead_time  INT          NOT NULL,          -- days
    capacity_per_month INT          NOT NULL DEFAULT 10000,
    is_active          TINYINT(1)   NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS products (
    product_id     INT AUTO_INCREMENT PRIMARY KEY,
    product_name   VARCHAR(120) NOT NULL,
    category       VARCHAR(80)  NOT NULL,
    unit_price     DECIMAL(10,2) NOT NULL,
    daily_usage    INT NOT NULL,
    reorder_point  INT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id        INT AUTO_INCREMENT PRIMARY KEY,
    product_id          INT NOT NULL,
    warehouse_location  VARCHAR(120) NOT NULL,
    stock_quantity      INT NOT NULL,
    last_updated        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id       INT AUTO_INCREMENT PRIMARY KEY,
    vessel_name       VARCHAR(120) NOT NULL,
    supplier_id       INT NOT NULL,
    product_id        INT NOT NULL,
    quantity          INT NOT NULL,
    origin_port       VARCHAR(120) NOT NULL,
    destination_port  VARCHAR(120) NOT NULL,
    status            VARCHAR(40)  NOT NULL DEFAULT 'In Transit',
    progress          DECIMAL(4,3) NOT NULL DEFAULT 0,   -- 0.000 - 1.000 of the voyage
    delay_days        INT NOT NULL DEFAULT 0,
    eta               DATE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS risk_events (
    event_id        INT AUTO_INCREMENT PRIMARY KEY,
    event_type      VARCHAR(80)  NOT NULL,
    location        VARCHAR(120) NOT NULL,
    severity_score  INT NOT NULL,                       -- 0 - 100
    risk_level      VARCHAR(20)  NOT NULL DEFAULT 'LOW',
    description     VARCHAR(500),
    detected_by     VARCHAR(80)  NOT NULL DEFAULT 'System',
    status          VARCHAR(20)  NOT NULL DEFAULT 'Active',
    detected_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    order_id      INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id   INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL,
    total_price   DECIMAL(12,2) NOT NULL,
    order_status  VARCHAR(40) NOT NULL DEFAULT 'Pending Approval',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS agent_decisions (
    decision_id           INT AUTO_INCREMENT PRIMARY KEY,
    agent_name            VARCHAR(80)  NOT NULL,
    decision_type         VARCHAR(80)  NOT NULL,
    decision_description  VARCHAR(1000) NOT NULL,
    created_at            DATETIME DEFAULT CURRENT_TIMESTAMP
);
