"""Optional Streamlit entrypoint for GitHub demonstration.

Run locally once dependencies are installed:
    streamlit run streamlit_app.py
"""

import streamlit as st

from metrics import compute_metrics, load_rows

st.set_page_config(page_title="KPI Reporting Dashboard", layout="wide")
rows = load_rows()
summary, category_rows, daily_rows, priority_rows, alerts = compute_metrics(rows)

st.title("Executive KPI Reporting Dashboard")
st.caption("Applied analytics and decision-support demo")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Tickets", summary["ticket_count"])
col2.metric("Avg. Resolution", f"{summary['average_resolution_hours']}h")
col3.metric("SLA Compliance", f"{summary['sla_compliance_rate']:.0%}")
col4.metric("Reopened Rate", f"{summary['reopened_rate']:.0%}")
col5.metric("Health Score", summary["operations_health_score"])

st.subheader("Performance by Category")
st.dataframe(category_rows, use_container_width=True)

st.subheader("Performance by Priority")
st.dataframe(priority_rows, use_container_width=True)

st.subheader("Daily Operations View")
st.dataframe(daily_rows, use_container_width=True)

st.subheader("Alert Digest")
st.dataframe(alerts, use_container_width=True)
