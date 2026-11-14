-- Demo seed data. Portable between MySQL and SQLite.

INSERT INTO suppliers (supplier_name, country, product_category, reliability_score, price_index, average_lead_time, capacity_per_month) VALUES
('ABC Microchips',          'Taiwan',      'Semiconductor', 0.960, 41.50, 12, 20000),
('Pacific Silicon Works',   'South Korea', 'Semiconductor', 0.910, 38.00, 15, 15000),
('Shenzhen ChipTech',       'China',       'Semiconductor', 0.840, 33.75, 18, 30000),
('Bavaria Electronics',     'Germany',     'Semiconductor', 0.930, 47.20, 9,  8000),
('Lithium Energy Co',       'China',       'Battery',       0.880, 92.00, 20, 12000),
('Nordic Cell Systems',     'Sweden',      'Battery',       0.940, 108.50, 14, 6000),
('Deccan Power Cells',      'India',       'Battery',       0.900, 86.40, 16, 9000),
('Osaka Display Corp',      'Japan',       'Display',       0.950, 64.00, 11, 10000),
('Saigon Panel Industries', 'Vietnam',     'Display',       0.820, 52.30, 19, 14000),
('Rhine Steel Components',  'Germany',     'Chassis',       0.970, 22.10, 10, 25000),
('Pune Precision Metals',   'India',       'Chassis',       0.890, 17.80, 13, 30000);

INSERT INTO products (product_name, category, unit_price, daily_usage, reorder_point) VALUES
('Semiconductor', 'Semiconductor', 45.00, 120, 1200),
('Battery Pack',  'Battery',       100.00, 40, 400),
('OLED Display',  'Display',       60.00, 75, 750),
('Chassis Frame', 'Chassis',       20.00, 90, 900);

INSERT INTO inventory (product_id, warehouse_location, stock_quantity) VALUES
(1, 'Chennai Warehouse',   540),
(2, 'Chennai Warehouse',   1650),
(3, 'Rotterdam Warehouse', 600),
(4, 'Hamburg Warehouse',   4200);

INSERT INTO shipments (vessel_name, supplier_id, product_id, quantity, origin_port, destination_port, status, progress, delay_days, eta) VALUES
('Evergreen Ace',   1, 1, 1500, 'Kaohsiung Port', 'Chennai Port',     'In Transit', 0.45, 0, '2026-11-22'),
('Maersk Horizon',  5, 2, 800,  'Shanghai Port',  'Chennai Port',     'Delayed',    0.30, 4, '2026-11-29'),
('COSCO Pioneer',   8, 3, 1200, 'Busan Port',     'Rotterdam Port',   'In Transit', 0.62, 0, '2026-11-25'),
('MSC Aurora',      10, 4, 6000, 'Hamburg Port',  'Los Angeles Port', 'In Transit', 0.20, 0, '2026-12-03'),
('ONE Harmony',     2, 1, 800,  'Busan Port',     'Los Angeles Port', 'Customs Hold', 0.95, 2, '2026-11-18'),
('Hapag Meridian',  9, 3, 600,  'Singapore Port', 'Hamburg Port',     'In Transit', 0.10, 0, '2026-12-10');

INSERT INTO risk_events (event_type, location, severity_score, risk_level, description, detected_by) VALUES
('Port Congestion', 'Shanghai Port',  64, 'HIGH',   'Vessel queue above 40 ships; average berth wait 3.5 days', 'Logistics Agent'),
('Supplier Delay',  'Taiwan',         35, 'MEDIUM', 'Wafer fab maintenance may delay two weekly batches',      'Risk Agent');

INSERT INTO purchase_orders (supplier_id, product_id, quantity, total_price, order_status) VALUES
(10, 4, 2000, 44200.00, 'Approved');

INSERT INTO purchase_orders (supplier_id, product_id, quantity, total_price, order_status, created_at) VALUES
(8,  3, 500,  32000.00, 'Delivered', '2026-01-15 10:00:00');

INSERT INTO agent_decisions (agent_name, decision_type, decision_description) VALUES
('Procurement Agent', 'Purchase Order', 'Ordered 2000 x Chassis Frame from Rhine Steel Components (reliability 0.97)'),
('Logistics Agent',   'Disruption Response', 'Flagged congestion at Shanghai Port; monitoring Maersk Horizon delay');
