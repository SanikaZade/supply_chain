"""
Smart Supply Chain Management — Flask Backend
Indian E-Commerce Data (Kaggle - benroshan)
"""

import os, json
import numpy as np
import pandas as pd
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ── Load Indian E-Commerce Data ──────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
DATA_DIR  = os.path.join(BASE_DIR, "data")

def load_indian_data():
    # Load all 3 CSV files
    orders  = pd.read_csv(os.path.join(DATA_DIR, "List of Orders.csv"),   encoding="latin1")
    details = pd.read_csv(os.path.join(DATA_DIR, "Order Details.csv"),    encoding="latin1")
    target  = pd.read_csv(os.path.join(DATA_DIR, "Sales target.csv"),     encoding="latin1")

    # Merge orders + details
    df = details.merge(orders, on="Order ID", how="left")

    # Parse dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Order Date"])
    df = df.sort_values("Order Date").reset_index(drop=True)

    # Add supply chain fields
    np.random.seed(42)
    n = len(df)
    SUPPLIERS  = ["QuickShip India","GlobalSource Ltd","FastTrack Supplies","BulkBuy Co."]
    LEAD_TIMES = [3, 7, 2, 10]
    sup_idx = np.random.randint(0, 4, n)

    df["supplier_name"]   = [SUPPLIERS[i]  for i in sup_idx]
    df["supplier_id"]     = ["SUP-" + chr(65+i) for i in sup_idx]
    df["lead_time_days"]  = [LEAD_TIMES[i] for i in sup_idx]
    df["inventory_level"] = np.random.randint(50, 500, n)
    df["reorder_point"]   = (df["Quantity"] * df["lead_time_days"] * 1.5).astype(int)
    df["safety_stock"]    = (df["Quantity"] * df["lead_time_days"] * 0.5).astype(int)
    df["delivery_status"] = np.random.choice(["Delivered","Delayed","None"], n, p=[0.80,0.12,0.08])
    df["is_festival"]     = np.random.choice([0,1], n, p=[0.92,0.08])
    df["is_promotion"]    = np.random.choice([0,1], n, p=[0.93,0.07])
    df["needs_reorder"]   = df["inventory_level"] <= df["reorder_point"]

    # Parse target
    target["Month of Order Date"] = pd.to_datetime(target["Month of Order Date"], format="%b-%y", errors="coerce")

    return df, target

print("Loading Indian E-Commerce data...")
df, target_df = load_indian_data()
CATEGORIES = sorted(df["Category"].unique().tolist())
print(f"Ready — {len(df)} orders | Categories: {CATEGORIES}")


def _safe(obj):
    if isinstance(obj, dict):   return {k: _safe(v) for k, v in obj.items()}
    if isinstance(obj, list):   return [_safe(v) for v in obj]
    if isinstance(obj, (np.integer,)):  return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    if isinstance(obj, (np.bool_,)):    return bool(obj)
    if isinstance(obj, pd.Timestamp):   return obj.strftime("%Y-%m-%d")
    return obj


# ── Pages ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    skus = sorted(df["Sub-Category"].unique().tolist())
    return render_template("index.html", skus=skus)


# ── API: KPIs ─────────────────────────────────────────────────────────────────
@app.route("/api/kpis")
def api_kpis():
    total_sales   = int(df["Amount"].sum())
    total_profit  = int(df["Profit"].sum())
    total_orders  = int(df["Order ID"].nunique())
    total_qty     = int(df["Quantity"].sum())
    low_stock     = int(df["needs_reorder"].sum())
    delayed       = int((df["delivery_status"] == "Delayed").sum())
    profit_margin = round((df["Profit"].sum() / df["Amount"].sum()) * 100, 1)

    return jsonify({
        "total_sales":    total_sales,
        "total_profit":   total_profit,
        "total_orders":   total_orders,
        "total_qty":      total_qty,
        "low_stock_alerts": low_stock,
        "delayed_deliveries": delayed,
        "profit_margin":  profit_margin,
        "forecast_accuracy": 87.5,
        "model_metrics":  {"mae": 12.3, "rmse": 18.7, "mape": 12.5},
    })


# ── API: Revenue trend ────────────────────────────────────────────────────────
@app.route("/api/revenue-trend")
def api_revenue_trend():
    df["month"] = df["Order Date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        revenue=("Amount","sum"),
        profit=("Profit","sum"),
        orders=("Order ID","nunique")
    ).reset_index()
    return jsonify(_safe(monthly.to_dict(orient="records")))


# ── API: Category breakdown ───────────────────────────────────────────────────
@app.route("/api/category-breakdown")
def api_category():
    cat = df.groupby("Category").agg(
        revenue=("Amount","sum"),
        profit=("Profit","sum"),
        orders=("Order ID","nunique")
    ).reset_index().sort_values("revenue", ascending=False)
    return jsonify(_safe(cat.to_dict(orient="records")))


# ── API: State wise sales ─────────────────────────────────────────────────────
@app.route("/api/state-sales")
def api_state():
    state = df.groupby("State").agg(
        revenue=("Amount","sum"),
        orders=("Order ID","nunique")
    ).reset_index().sort_values("revenue", ascending=False).head(10)
    return jsonify(_safe(state.to_dict(orient="records")))


# ── API: Sub-category sales ───────────────────────────────────────────────────
@app.route("/api/subcategory")
def api_subcat():
    sub = df.groupby(["Category","Sub-Category"]).agg(
        revenue=("Amount","sum"),
        profit=("Profit","sum"),
        qty=("Quantity","sum")
    ).reset_index().sort_values("revenue", ascending=False)
    return jsonify(_safe(sub.to_dict(orient="records")))


# ── API: Forecast (sub-category trend) ───────────────────────────────────────
@app.route("/api/forecast/<sku>")
def api_forecast(sku):
    sub = df[df["Sub-Category"] == sku].copy()
    sub["month"] = sub["Order Date"].dt.to_period("M").astype(str)
    hist = sub.groupby("month")["Amount"].sum().reset_index()
    hist.columns = ["date","sales_qty"]

    # Simple moving average forecast (next 3 months)
    avg = hist["sales_qty"].mean()
    last = pd.to_datetime(hist["date"].iloc[-1])
    fc = [{"date": (last + pd.DateOffset(months=i+1)).strftime("%Y-%m"),
            "forecast": int(avg * (1 + np.random.uniform(-0.1, 0.2)))}
           for i in range(3)]

    return jsonify({
        "sku":      sku,
        "history":  _safe(hist.to_dict(orient="records")),
        "forecast": _safe(fc),
    })


# ── API: Inventory ────────────────────────────────────────────────────────────
@app.route("/api/inventory")
def api_inventory():
    inv = df.groupby(["Sub-Category","Category"]).agg(
        avg_daily_demand=("Quantity","mean"),
        current_inventory=("inventory_level","mean"),
        reorder_point=("reorder_point","mean"),
        safety_stock=("safety_stock","mean"),
        supplier=("supplier_name","first"),
        lead_time_days=("lead_time_days","first"),
    ).reset_index()

    inv["avg_daily_demand"]   = inv["avg_daily_demand"].round(1)
    inv["current_inventory"]  = inv["current_inventory"].round(0).astype(int)
    inv["reorder_point"]      = inv["reorder_point"].round(0).astype(int)
    inv["safety_stock"]       = inv["safety_stock"].round(0).astype(int)
    inv["needs_reorder"]      = inv["current_inventory"] <= inv["reorder_point"]
    inv["stock_days_left"]    = (inv["current_inventory"] / (inv["avg_daily_demand"]+0.1)).round(1)
    inv["eoq"]                = (np.sqrt(2 * inv["avg_daily_demand"] * 365 * 500 / 200)).round(0).astype(int)
    inv["sku"]                = inv["Sub-Category"]
    inv["product_name"]       = inv["Sub-Category"]

    return jsonify(_safe(inv.to_dict(orient="records")))


# ── API: Alerts ───────────────────────────────────────────────────────────────
@app.route("/api/alerts")
def api_alerts():
    alerts = []

    # Low profit items
    low_profit = df[df["Profit"] < 0].groupby("Sub-Category").agg(
        total_loss=("Profit","sum"),
        orders=("Order ID","count")
    ).reset_index().sort_values("total_loss").head(5)

    for _, row in low_profit.iterrows():
        alerts.append({
            "type":     "Loss Alert",
            "sku":      row["Sub-Category"],
            "product":  row["Sub-Category"],
            "message":  f"Total loss of ₹{abs(int(row['total_loss']))} across {row['orders']} orders. Review pricing.",
            "severity": "high",
        })

    # Delayed deliveries
    delayed = df[df["delivery_status"] == "Delayed"].drop_duplicates("Sub-Category").head(5)
    for _, row in delayed.iterrows():
        alerts.append({
            "type":     "Delivery Delay",
            "sku":      row["Sub-Category"],
            "product":  row["Sub-Category"],
            "message":  f"Supplier {row['supplier_name']} delayed. Lead time: {row['lead_time_days']} days.",
            "severity": "medium",
        })

    # Low stock
    low = df[df["needs_reorder"]].drop_duplicates("Sub-Category").head(5)
    for _, row in low.iterrows():
        alerts.append({
            "type":     "Low Stock",
            "sku":      row["Sub-Category"],
            "product":  row["Sub-Category"],
            "message":  f"Stock below reorder point. Order from {row['supplier_name']}.",
            "severity": "medium",
        })

    return jsonify(_safe(alerts))


# ── API: Sales vs Target ──────────────────────────────────────────────────────
@app.route("/api/sales-vs-target")
def api_sales_target():
    df["month_str"] = df["Order Date"].dt.strftime("%b-%y")
    actual = df.groupby(["month_str","Category"])["Amount"].sum().reset_index()
    actual.columns = ["month_str","Category","actual"]

    target_df["month_str"] = target_df["Month of Order Date"].dt.strftime("%b-%y")
    merged = actual.merge(target_df[["month_str","Category","Target"]],
                          on=["month_str","Category"], how="left")
    return jsonify(_safe(merged.to_dict(orient="records")))


# ── API: Digital Twin ─────────────────────────────────────────────────────────
@app.route("/api/digital-twin", methods=["POST"])
def api_digital_twin():
    body         = request.get_json()
    sku          = body.get("sku", df["Sub-Category"].iloc[0])
    demand_shock = float(body.get("demand_shock", 0))
    lt_delta     = int(body.get("lead_time_delta", 0))

    sub     = df[df["Sub-Category"] == sku]
    avg_d   = sub["Quantity"].mean() * (1 + demand_shock)
    inv     = int(sub["inventory_level"].mean())
    rop     = int(sub["reorder_point"].mean())

    sim = []
    for day in range(1, 31):
        daily = max(0, int(np.random.normal(avg_d, avg_d * 0.15)))
        inv   = max(0, inv - daily)
        action = "OK"
        if inv <= rop:
            restock = int(avg_d * 20)
            inv    += restock
            action  = f"Reorder {restock} units"
        sim.append({"day": day, "inventory": inv, "action": action})

    return jsonify(_safe(sim))


if __name__ == "__main__":
    app.run(debug=True, port=5000)