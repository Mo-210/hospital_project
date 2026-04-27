# 🏥 Hospital Operations & Revenue Cycle Analysis (2023)

## 🔗 Live Demo
- Streamlit Dashboard: [Open App](https://mo-210-hospital-project-dashboardapp-39muk9.streamlit.app/)

## 📋 Project Overview
This project evaluates hospital performance using a Kaggle dataset to address a clear business challenge: **high clinical volume vs. low cash collection**.  
It delivers a full pipeline, from raw CSV files to an interactive **Business Intelligence (BI) dashboard**, to connect clinical operations with financial outcomes.

## 🚀 Key Achievements & Insights
- **End-to-End Data Engineering:** Built an ETL workflow to move CSV data into a relational **SQLite** database for reliable SQL analysis.
- **Revenue Cycle Management (RCM):** Measured **31.5% collection efficiency**, highlighting "Pending" and "Failed" payments as major cash-flow leaks.
- **Operational Optimization:** Analyzed physician workload and appointment outcomes to surface utilization bottlenecks.
- **Patient Demographics Analysis:** Built age-group and registration trend logic to explain demand patterns by patient segment.
- **Interactive BI Dashboard:** Developed a multi-page **Streamlit** dashboard with practical filtering for executive KPI tracking.

## 📊 Dashboard Key Features
- **Executive Overview:** Tracks gross revenue, net collections, and collection efficiency.
- **Clinical Operations:** Shows physician profiles with **patient volume vs. average treatment cost**.
- **Revenue Cycle:** Breaks down insurance performance and payment method mix.
- **Patient Insights:** Visualizes age distribution and monthly growth in new registrations.

## 📁 Project Directory
- `dashboard/app.py`: Interactive Streamlit BI application.
- `notebooks/Hospital_Performance_Analysis.ipynb`: Core exploratory data analysis (EDA) workflow.
- `notebooks/archive/project.ipynb`: Archived exploratory notebook retained for historical reference.
- `reports/REPORT.md`: Executive report with strategic recommendations.
- `data/`: Raw CSV files and the final `hospital.db`.

## ⚙️ Quick Start
1. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the SQLite database (if needed)**
   ```bash
   python scripts/build_sqlite_from_csv.py
   ```

3. **Run the dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

## 🖥️ Run Dashboard
1. Open sidebar navigation to select a page.
2. Use `Reporting Period` to filter by month.
3. Export filtered billing data with `Export Billing View to CSV`.

For detailed dashboard usage notes, see `dashboard/HOW_TO_USE.md`.
For a full project tree, see `PROJECT_STRUCTURE.md`.

## 🧾 Notebook Versioning Note
- `notebooks/Hospital_Performance_Analysis.ipynb` is the canonical, portfolio-ready notebook.
- `notebooks/archive/project.ipynb` is kept only as an archived exploratory snapshot.