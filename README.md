# ChainIQ — Smart Supply Chain Management System
### AI + Digital Twin | Retail / E-commerce | College Project

---

## 📁 Project Structure

```
supply_chain/
├── app.py                  ← Flask backend (all API routes)
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Cloud-ready container
├── docker-compose.yml      ← One-command deployment
├── data/
│   ├── generate_data.py    ← Synthetic dataset generator
│   └── supply_chain_data.csv  ← Generated automatically
├── models/
│   └── ai_engine.py        ← XGBoost forecasting + optimization + anomaly detection
└── templates/
    └── index.html          ← Full dashboard UI
```

---

## 🚀 Quick Start (Local)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate dataset
```bash
python data/generate_data.py
```

### 3. Run the app
```bash
python app.py
```

### 4. Open browser
```
http://localhost:5000
```

---

## 🐳 Cloud Deployment (Docker)

```bash
# Build and run
docker-compose up --build

# Access at
http://localhost:5000
```

To deploy on a cloud VM (AWS EC2 / GCP / Azure):
```bash
# On the server
git clone <your-repo>
cd supply_chain
docker-compose up -d --build
```

---

## 🧠 AI Modules

| Module | Algorithm | Purpose |
|---|---|---|
| Demand Forecasting | XGBoost | Predict next 30 days of sales per SKU |
| Inventory Optimization | EOQ + Safety Stock | Calculate optimal reorder quantity |
| Anomaly Detection | Isolation Forest | Flag unusual demand/delivery events |
| Digital Twin | Monte Carlo Simulation | What-if scenario planning |

---

## 📊 Dashboard Sections

1. **Dashboard** — KPI cards + revenue trend + category breakdown
2. **Demand Forecast** — Per-SKU 30-day AI forecast vs historical
3. **Inventory** — Safety stock, EOQ, reorder decisions for all SKUs
4. **Alerts** — Low stock, delayed delivery, anomaly alerts
5. **Digital Twin** — Simulate demand shocks and lead time delays

---

## 📈 Key Formulas Used

```
Safety Stock  = Z × σ_demand × √(lead_time)     [Z = 1.65 → 95% service level]
Reorder Point = avg_demand × lead_time + safety_stock
EOQ           = √(2 × D × S / H)
```

---

## 🛠 Tech Stack

- **Backend**: Python Flask
- **AI/ML**: XGBoost, Isolation Forest (scikit-learn)
- **Frontend**: Vanilla JS + Chart.js
- **Data**: Pandas, NumPy
- **Deployment**: Docker + Docker Compose (cloud-ready)

---

## 🔮 Digital Twin — What-If Scenarios

The Digital Twin simulator lets you:
- Simulate +/- demand shocks (e.g. festival spike, recession dip)
- Add supplier lead time delays
- See live 30-day inventory projection with automatic reorder triggers

---

## 📋 Dataset Fields

| Field | Description |
|---|---|
| sku | Product identifier |
| date | Daily date |
| sales_qty | Units sold |
| inventory_level | Units in stock |
| reorder_point | Trigger threshold |
| safety_stock | Buffer stock |
| lead_time_days | Supplier delivery time |
| supplier_id / name | Supplier details |
| delivery_status | Delivered / Delayed / None |
| is_festival | Festival day flag |
| is_promotion | Promotion day flag |
| is_anomaly | Injected anomaly flag |
| revenue | Daily revenue (₹) |

---

## 👨‍💻 Developed For
**Final Year Engineering Project** — AI and Allied Systems
Domain: Retail / E-commerce Supply Chain
