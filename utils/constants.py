"""Supply chain constants (values come from config.yaml where possible)."""

from app.settings import get_settings

_settings = get_settings()

MAX_BUDGET = _settings.get("budget.monthly_limit", 100000)
MAX_SINGLE_ORDER = _settings.get("budget.max_single_order", 60000)
CRITICAL_STOCK_DAYS = _settings.get("inventory.critical_stock_days", 5)
WARNING_STOCK_DAYS = _settings.get("inventory.warning_stock_days", 10)
TARGET_COVER_DAYS = _settings.get("inventory.target_cover_days", 30)
DEFAULT_DAILY_USAGE = 100

PORTS = _settings.ports
MAJOR_PORTS = [p["name"] for p in PORTS]
PORT_COORDS = {p["name"]: (p["lat"], p["lon"]) for p in PORTS}

ORDER_STATUSES = ["Pending Approval", "Approved", "Rejected", "Shipped", "Delivered"]
OPEN_ORDER_STATUSES = ("Pending Approval", "Approved", "Shipped")
PORT_COUNTRY = {p["name"]: p.get("country") for p in PORTS}
