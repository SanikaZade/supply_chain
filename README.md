#  AI-Powered Smart Supply Chain Management System

> An intelligent Supply Chain Management System built with Python, Flask, and Machine Learning to help businesses forecast demand, optimize inventory, detect anomalies, and improve decision-making through data-driven insights.

---

##  About the Project

Managing a supply chain efficiently is challenging due to unpredictable customer demand, inventory fluctuations, and operational risks. Businesses often struggle with balancing stock levels while maintaining customer satisfaction and minimizing costs.

This project was developed to address these challenges by combining **data analytics**, **machine learning**, and **interactive visualization** into a single web application. It analyzes historical sales data, provides inventory recommendations, identifies unusual business patterns, and presents meaningful insights through an easy-to-use dashboard.

The goal of this project is to demonstrate how AI can support smarter supply chain decisions and improve operational efficiency.

---

##  What This Project Can Do

-  Analyze historical sales data
-  Forecast future product demand
-  Optimize inventory levels
-  Calculate reorder points
-  Estimate safety stock
-  Detect unusual sales or inventory behavior
-  Simulate supply chain scenarios using a Digital Twin concept
-  Display business insights through interactive dashboards

---

##  Machine Learning & Analytics

This project combines traditional inventory management techniques with machine learning algorithms to improve business decisions.

### Demand Forecasting
Predicts future demand based on historical sales patterns, helping businesses prepare inventory more effectively.

### Inventory Optimization
Calculates optimal inventory values using:

- Economic Order Quantity (EOQ)
- Safety Stock
- Reorder Point

### Anomaly Detection
Uses machine learning techniques to identify abnormal sales trends and unusual inventory behavior.

### Digital Twin Simulation
Simulates supply chain performance under different business conditions to support planning and decision-making.

---


# System Workflow

```
                CSV Dataset
                     │
                     ▼
           Data Preprocessing
              (Pandas / NumPy)
                     │
                     ▼
         Machine Learning Engine
       ┌──────────┬──────────────┐
       │          │              │
       ▼          ▼              ▼
 Demand     Inventory      Anomaly
Forecast   Optimization   Detection
       │          │              │
       └──────────┴──────────────┘
                     │
                     ▼
          Digital Twin Simulation
                     │
                     ▼
             Flask Web Application
                     │
                     ▼
         Interactive Dashboard
```

---

##  Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, XGBoost |
| Data Visualization | Chart.js |
| Deployment | Docker, Docker Compose, Gunicorn |

---
## 📸 Application Preview

<img width="1665" height="840" alt="Screenshot 2026-07-02 112549" src="https://github.com/user-attachments/assets/5ba20c54-409e-4a4f-b8d4-cbabc118bf4b" />

<img width="1627" height="402" alt="Screenshot 2026-07-02 123618" src="https://github.com/user-attachments/assets/052bae70-c6f0-4869-ae0c-0024a3e45dc2" />


##  Project Structure

```text
Supply_Chain_Project/

├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── data/
│   ├── List of Orders.csv
│   ├── Order Details.csv
│   └── Sales target.csv
│
├── models/
│   └── ai_engine.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```

---

##  Dashboard Highlights

The dashboard provides a simple and interactive view of business performance, including:

- Sales Overview
- Revenue Analysis
- Product Demand Trends
- Inventory Status
- Forecast Results
- Inventory Optimization Metrics
- Supply Chain Alerts
- Digital Twin Simulation

---

##  Dataset

The project uses an Indian E-Commerce dataset containing information such as:

- Customer Orders
- Product Details
- Sales Records
- Order Information
- Regional Sales
- Sales Targets

Dataset Files:

- `List of Orders.csv`
- `Order Details.csv`
- `Sales target.csv`

---

##  Project Highlights

✔ AI-powered demand forecasting

✔ Inventory optimization using EOQ and Safety Stock

✔ Interactive business dashboard

✔ Machine learning-based anomaly detection

✔ Digital Twin concept for supply chain simulation

✔ Docker-ready application

---

##  Future Improvements

Some planned enhancements include:

- Real-time data integration
- Multi-warehouse inventory management
- Supplier performance analytics
- Live shipment tracking
- REST API support
- User authentication
- Cloud deployment (AWS/Azure)
- Advanced forecasting models
- Power BI integration


