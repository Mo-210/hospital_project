# Dashboard - How To Use

## 1) Open project folder
Make sure your terminal is in the project root:

```bash
cd hospital_project
```

## 2) Install required packages (first time only)

```bash
pip install -r requirements.txt
```

## 3) Run the dashboard

```bash
streamlit run dashboard/app.py
```

## 4) Use the dashboard
- Select page from sidebar navigation.
- Apply `Reporting Period` filter from the sidebar.
- Export filtered billing data using `Export Billing View to CSV`.

## Notes
- Dashboard data source is: `data/hospital.db`
- If database is missing, rebuild it from CSV files:

```bash
python scripts/build_sqlite_from_csv.py
```
