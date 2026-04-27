from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# --- DATA ACCESS LAYER ---
def get_db_path() -> Path:
    """Locate the SQLite database file."""
    here = Path(__file__).resolve().parent
    return here.parent / "data" / "hospital.db"

@st.cache_data(ttl=600)
def load_hospital_data(db_path: Path) -> dict[str, pd.DataFrame]:
    """Efficiently fetch and cache database tables."""
    conn_str = f"sqlite:///{db_path.as_posix()}"
    tables = ["patients", "doctors", "appointments", "treatments", "billing"]
    raw_data = {t: pd.read_sql(f"SELECT * FROM {t}", conn_str) for t in tables}
    
    # Standardize time series and data types
    raw_data["billing"]["bill_date"] = pd.to_datetime(raw_data["billing"]["bill_date"])
    raw_data["billing"]["bill_month"] = raw_data["billing"]["bill_date"].dt.strftime('%Y-%m')
    raw_data["appointments"]["appointment_date"] = pd.to_datetime(raw_data["appointments"]["appointment_date"])
    raw_data["appointments"]["appt_month"] = raw_data["appointments"]["appointment_date"].dt.strftime('%Y-%m')
    raw_data["patients"]["registration_date"] = pd.to_datetime(raw_data["patients"]["registration_date"])
    raw_data["patients"]["reg_month"] = raw_data["patients"]["registration_date"].dt.strftime('%Y-%m')
    
    # Calculate Age for demographics
    current_year = pd.Timestamp.now().year
    raw_data["patients"]["year_of_birth"] = pd.to_datetime(raw_data["patients"]["date_of_birth"]).dt.year
    raw_data["patients"]["age"] = current_year - raw_data["patients"]["year_of_birth"]
    
    return raw_data

# --- VIEW: EXECUTIVE SUMMARY ---
def show_executive_summary(data: dict):
    st.subheader("Executive Financial Performance")
    billing = data["billing"]
    
    total_billed = billing["amount"].sum()
    total_paid = billing[billing["payment_status"] == "Paid"]["amount"].sum()
    efficiency = (total_paid / total_billed * 100) if total_billed > 0 else 0
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Gross Revenue", f"${total_billed:,.0f}")
    kpi2.metric("Net Collections", f"${total_paid:,.0f}")
    kpi3.metric("Collection Efficiency", f"{efficiency:.1f}%")
    
    st.markdown("---")
    
    # Revenue Trend (Stacked Bar)
    trend = (
        billing.assign(
            paid=lambda x: x["amount"].where(x["payment_status"] == "Paid", 0),
            outstanding=lambda x: x["amount"].where(x["payment_status"] != "Paid", 0)
        )
        .groupby("bill_month")
        .agg(Paid=("paid", "sum"), Outstanding=("outstanding", "sum"))
        .reset_index()
    )
    
    fig_trend = px.bar(
        trend, x="bill_month", y=["Paid", "Outstanding"],
        title="Monthly Revenue Realization (USD)",
        color_discrete_map={"Paid": "#2E7D32", "Outstanding": "#EF6C00"},
        barmode="group", labels={"bill_month": "Month", "value": "Revenue ($)"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- VIEW: CLINICAL OPERATIONS ---
def show_clinical_ops(data: dict):
    st.subheader("Clinical Volume & Physician Utilization")
    
    docs = data["doctors"].copy()
    docs["full_name"] = docs["first_name"] + " " + docs["last_name"]
    appts = data["appointments"]
    treats = data["treatments"]
    
    # Doctor Workload Analysis
    doc_metrics = (
        appts.merge(docs, on="doctor_id")
        .merge(treats, on="appointment_id", how="left")
        .groupby(["full_name", "specialization"])
        .agg(
            volume=("appointment_id", "count"),
            unique_patients=("patient_id", "nunique"),
            avg_cost=("cost", "mean")
        )
        .reset_index()
        .sort_values("volume", ascending=False)
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Scatter Plot from Notebook: Volume vs Economics
        fig_scatter = px.scatter(
            doc_metrics, x="unique_patients", y="avg_cost",
            size="volume", color="specialization", hover_name="full_name",
            title="Physician Profile: Volume vs. Avg Treatment Cost",
            labels={"unique_patients": "Unique Patients", "avg_cost": "Avg Cost ($)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col2:
        # Appointment Status (No-show analysis)
        status_mix = appts["status"].value_counts().reset_index()
        fig_status = px.pie(status_mix, values="count", names="status", 
                            title="Appointment Outcomes", hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)

    st.markdown("---")
    st.subheader("Service Line Analysis")
    st.caption(
        "Goal: show which treatment types drive most revenue, so priorities for growth and margin protection are clear."
    )

    # Treatment Mix
    treat_mix = treats.groupby("treatment_type").agg(
        Count=("treatment_id", "count"),
        Revenue=("cost", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)

    total_revenue = treat_mix["Revenue"].sum()
    treat_mix["Revenue Share %"] = (treat_mix["Revenue"] / total_revenue * 100).round(1)
    treat_mix["Share Label"] = treat_mix["Revenue Share %"].astype(str) + "%"

    fig_treat = px.bar(
        treat_mix,
        x="treatment_type",
        y="Revenue",
        color="Revenue Share %",
        text="Share Label",
        title="Service Line Revenue Contribution (with Share %)",
        labels={
            "Revenue": "Total Revenue ($)",
            "treatment_type": "Service Line",
            "Revenue Share %": "Revenue Share (%)",
        },
    )
    fig_treat.update_traces(textposition="outside")
    fig_treat.update_layout(yaxis_tickprefix="$")
    st.plotly_chart(fig_treat, use_container_width=True)

# --- VIEW: REVENUE CYCLE MANAGEMENT (RCM) ---
def show_rcm_deep_dive(data: dict):
    st.subheader("Revenue Cycle & Payer Analytics")
    
    billing = data["billing"]
    patients = data["patients"]
    
    # Merge Billing with Patients for Insurance Data
    billing_with_ins = billing.merge(
        patients[["patient_id", "insurance_provider"]], 
        on="patient_id", how="left"
    ).fillna({"insurance_provider": "Self-Pay"})
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Insurance Revenue
        ins_perf = billing_with_ins.groupby("insurance_provider")["amount"].sum().reset_index()
        fig_ins = px.bar(ins_perf.sort_values("amount"), x="amount", y="insurance_provider", 
                         orientation='h', title="Revenue by Insurance Provider")
        st.plotly_chart(fig_ins, use_container_width=True)
        
    with col2:
        # Payment Method Mix (From Notebook)
        method_mix = billing.groupby("payment_method")["amount"].sum().reset_index()
        fig_method = px.pie(method_mix, values="amount", names="payment_method", 
                            title="Revenue by Payment Method", hole=0.4)
        st.plotly_chart(fig_method, use_container_width=True)

    st.markdown("---")
    st.subheader("Collection Efficiency Detail")
    # Payment Status Breakdown
    status_billing = billing.groupby("payment_status").agg(
        Invoices=("bill_id", "count"),
        Total_Value=("amount", "sum")
    ).reset_index()
    
    fig_status_bill = px.bar(status_billing, x="payment_status", y="Total_Value", 
                             color="Invoices", title="Financial Exposure by Payment Status")
    st.plotly_chart(fig_status_bill, use_container_width=True)

# --- VIEW: PATIENT DEMOGRAPHICS ---
def show_patient_insights(data: dict):
    st.subheader("Patient Population Analysis")
    patients = data["patients"].copy()

    # Gender Distribution (show first)
    gender_dist = patients["gender"].value_counts().reset_index()
    fig_gender = px.pie(
        gender_dist,
        names="gender",
        values="count",
        title="Patient Gender Distribution",
        hole=0.45,
    )
    st.plotly_chart(fig_gender, use_container_width=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age Grouping
        bins = [0, 18, 35, 60, 100]
        labels = ['Under 18', '18-35', '36-60', '60+']
        patients['age_group'] = pd.cut(patients['age'], bins=bins, labels=labels)
        age_dist = patients['age_group'].value_counts().reset_index()
        fig_age = px.bar(age_dist, x='age_group', y='count', title="Patient Age Distribution",
                         color_discrete_sequence=['#3F51B5'])
        st.plotly_chart(fig_age, use_container_width=True)
        
    with col2:
        # Registration Trend (Growth)
        reg_trend = patients.groupby("reg_month").size().reset_index(name="new_patients")
        fig_reg = px.line(reg_trend, x="reg_month", y="new_patients", markers=True,
                          title="New Patient Acquisitions", labels={"reg_month": "Month"})
        st.plotly_chart(fig_reg, use_container_width=True)

# --- MAIN APPLICATION CONTROLLER ---
def main():
    st.set_page_config(page_title="HealthBI | Hospital Analytics", layout="wide", page_icon="🏥")
    
    db_path = get_db_path()
    if not db_path.exists():
        st.error(f"Data source not found at {db_path}")
        st.stop()

    raw_data = load_hospital_data(db_path)
    
    # Sidebar Navigation
    st.sidebar.title("🏥 Hospital BI")
    nav = st.sidebar.radio("Navigation", 
                           ["Executive Overview", "Clinical Operations", "Revenue Cycle", "Patient Demographics"])
    
    st.sidebar.markdown("---")
    st.sidebar.header("Global Filters")
    
    all_months = sorted(raw_data["billing"]["bill_month"].unique())
    period_start, period_end = st.sidebar.select_slider(
        "Reporting Period",
        options=all_months,
        value=(all_months[0], all_months[-1]),
    )
    start_idx = all_months.index(period_start)
    end_idx = all_months.index(period_end)
    selected_months = all_months[start_idx : end_idx + 1]
    
    # Smart Analysis Period Text
    if len(selected_months) == len(all_months):
        period_display = "Full Year 2023"
    else:
        period_display = f"{period_start} to {period_end}"

    # Filtering Data based on months
    filtered_data = raw_data.copy()
    filtered_data["billing"] = raw_data["billing"][raw_data["billing"]["bill_month"].isin(selected_months)].copy()
    filtered_data["appointments"] = raw_data["appointments"][
        raw_data["appointments"]["appt_month"].isin(selected_months)
    ].copy()

    # Keep treatment rows aligned with filtered appointments for operational views.
    filtered_appointment_ids = set(filtered_data["appointments"]["appointment_id"].unique())
    filtered_data["treatments"] = raw_data["treatments"][
        raw_data["treatments"]["appointment_id"].isin(filtered_appointment_ids)
    ].copy()

    # Keep patient demographics aligned with the selected registration period.
    filtered_data["patients"] = raw_data["patients"][
        raw_data["patients"]["reg_month"].isin(selected_months)
    ].copy()
    
    # Display UI
    st.title(f"{nav}")
    st.info(f"📅 **Analysis Period:** {period_display}")

    if nav == "Executive Overview":
        show_executive_summary(filtered_data)
    elif nav == "Clinical Operations":
        show_clinical_ops(filtered_data)
    elif nav == "Revenue Cycle":
        show_rcm_deep_dive(filtered_data)
    elif nav == "Patient Demographics":
        show_patient_insights(filtered_data)

    st.sidebar.markdown("---")
    csv = filtered_data["billing"].to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        "Export Billing View to CSV",
        data=csv,
        file_name="hospital_metrics.csv",
        mime="text/csv",
    )

if __name__ == "__main__":
    main()