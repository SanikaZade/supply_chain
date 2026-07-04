"""
AI Engine — Demand Forecasting + Inventory Optimization + Anomaly Detection
Uses XGBoost for forecasting and rule-based optimization.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")


# ──────────────────────────────────────────────
# 1. DATA LOADER
# ──────────────────────────────────────────────
def load_data(path="data/supply_chain_data.csv"):
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values(["sku", "date"]).reset_index(drop=True)
    return df


# ──────────────────────────────────────────────
# 2. FEATURE ENGINEERING
# ──────────────────────────────────────────────
def add_features(df):
    df = df.copy()
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"]        = df["date"].dt.month
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_weekend"]   = (df["day_of_week"] >= 5).astype(int)

    for sku in df["sku"].unique():
        mask = df["sku"] == sku
        s    = df.loc[mask, "sales_qty"]
        df.loc[mask, "lag_7"]    = s.shift(7)
        df.loc[mask, "lag_14"]   = s.shift(14)
        df.loc[mask, "lag_30"]   = s.shift(30)
        df.loc[mask, "roll_7"]   = s.shift(1).rolling(7).mean()
        df.loc[mask, "roll_14"]  = s.shift(1).rolling(14).mean()

    le = LabelEncoder()
    df["sku_enc"] = le.fit_transform(df["sku"])
    return df


# ──────────────────────────────────────────────
# 3. DEMAND FORECASTING (XGBoost)
# ──────────────────────────────────────────────
FEATURES = ["sku_enc", "day_of_week", "day_of_month", "month",
            "week_of_year", "is_weekend", "is_festival", "is_promotion",
            "lag_7", "lag_14", "lag_30", "roll_7", "roll_14"]

def train_forecast_model(df):
    from xgboost import XGBRegressor
    df_feat = add_features(df).dropna(subset=FEATURES)
    split   = int(len(df_feat) * 0.85)
    train   = df_feat.iloc[:split]
    test    = df_feat.iloc[split:]

    model = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.08,
                         subsample=0.8, colsample_bytree=0.8,
                         random_state=42, verbosity=0)
    model.fit(train[FEATURES], train["sales_qty"])

    preds = model.predict(test[FEATURES])
    mae   = mean_absolute_error(test["sales_qty"], preds)
    rmse  = np.sqrt(mean_squared_error(test["sales_qty"], preds))
    mape  = np.mean(np.abs((test["sales_qty"] - preds) /
                            (test["sales_qty"] + 1e-6))) * 100

    return model, {"mae": round(mae, 2), "rmse": round(rmse, 2),
                   "mape": round(mape, 2)}, test, preds


def forecast_next_30(df, model, sku):
    """Forecast next 30 days for a given SKU."""
    sku_df   = df[df["sku"] == sku].copy()
    last_date = sku_df["date"].max()

    future_rows = []
    for i in range(1, 31):
        future_date = last_date + pd.Timedelta(days=i)
        row = {
            "date": future_date,
            "sku": sku,
            "sales_qty": 0,
            "is_festival": 0,
            "is_promotion": 0,
        }
        future_rows.append(row)

    future_df = pd.DataFrame(future_rows)
    combined  = pd.concat([sku_df, future_df], ignore_index=True)
    combined  = add_features(combined)
    future_feat = combined.tail(30)[FEATURES].fillna(0)

    # encode sku
    sku_enc_val = combined["sku_enc"].dropna().iloc[0]
    future_feat["sku_enc"] = sku_enc_val

    preds = model.predict(future_feat)
    future_df["forecast"] = np.maximum(preds, 0).astype(int)
    return future_df[["date", "forecast"]]


# ──────────────────────────────────────────────
# 4. INVENTORY OPTIMIZATION
# ──────────────────────────────────────────────
def optimize_inventory(df):
    """Calculate safety stock, reorder point, EOQ, and recommendation per SKU."""
    results = []
    for sku in df["sku"].unique():
        s   = df[df["sku"] == sku].copy()
        avg = s["sales_qty"].mean()
        std = s["sales_qty"].std()
        lt  = s["lead_time_days"].iloc[0]

        # Z = 1.65 → 95% service level
        safety_stock  = round(1.65 * std * np.sqrt(lt))
        reorder_point = round(avg * lt + safety_stock)
        holding_cost  = s["unit_price"].iloc[0] * 0.20   # 20% annual holding
        order_cost    = 500                                # fixed order cost ₹
        annual_demand = avg * 365
        eoq           = round(np.sqrt((2 * annual_demand * order_cost) / holding_cost))
        current_inv   = s["inventory_level"].iloc[-1]
        needs_reorder = current_inv <= reorder_point

        results.append({
            "sku":             sku,
            "product_name":    s["product_name"].iloc[0],
            "category":        s["category"].iloc[0],
            "avg_daily_demand": round(avg, 1),
            "std_demand":      round(std, 1),
            "lead_time_days":  lt,
            "safety_stock":    int(safety_stock),
            "reorder_point":   int(reorder_point),
            "eoq":             int(eoq),
            "current_inventory": int(current_inv),
            "needs_reorder":   needs_reorder,
            "stock_days_left": round(current_inv / avg, 1) if avg > 0 else 999,
            "supplier":        s["supplier_name"].iloc[0],
        })
    return pd.DataFrame(results)


# ──────────────────────────────────────────────
# 5. ANOMALY DETECTION
# ──────────────────────────────────────────────
def detect_anomalies(df):
    """Isolation Forest on sales & inventory features."""
    feats = df[["sales_qty", "inventory_level"]].fillna(0)
    iso   = IsolationForest(contamination=0.04, random_state=42)
    df    = df.copy()
    df["anomaly_score"] = iso.fit_predict(feats)
    df["is_detected_anomaly"] = (df["anomaly_score"] == -1).astype(int)
    return df


# ──────────────────────────────────────────────
# 6. DIGITAL TWIN SIMULATION
# ──────────────────────────────────────────────
def run_digital_twin(df, sku, demand_shock=0.0, lead_time_delta=0):
    """
    Simulate 'what-if' scenarios on inventory over next 30 days.
    demand_shock: fractional change in demand (e.g. +0.5 = 50% more demand)
    lead_time_delta: extra days added to lead time
    """
    s       = df[df["sku"] == sku].copy()
    avg_d   = s["sales_qty"].mean() * (1 + demand_shock)
    std_d   = s["sales_qty"].std()
    lt      = s["lead_time_days"].iloc[0] + lead_time_delta
    ss      = round(1.65 * std_d * np.sqrt(lt))
    rop     = round(avg_d * lt + ss)
    inv     = s["inventory_level"].iloc[-1]
    rp      = s["unit_price"].iloc[0]

    sim_days, sim_inv, sim_actions = [], [], []
    for day in range(1, 31):
        daily_demand = max(0, int(np.random.normal(avg_d, std_d * 0.15)))
        inv          = max(0, inv - daily_demand)
        action       = "OK"
        if inv <= rop:
            from xgboost import XGBRegressor
            restock_qty = int(avg_d * 20)
            inv        += restock_qty
            action      = f"Reorder {restock_qty} units"
        sim_days.append(day)
        sim_inv.append(int(inv))
        sim_actions.append(action)

    return pd.DataFrame({"day": sim_days, "inventory": sim_inv, "action": sim_actions})
