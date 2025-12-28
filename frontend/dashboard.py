import streamlit as st
import requests
from sections.limits import render_limits


API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Quantum–Classical Market Risk",
    layout="wide",
)

STEP_LABELS = {
    "scenario_portfolio_risk.py": "Evaluating Distributions…",
    "risk_limits.py": "Evaluating Risk limits…",
    "backtesting.py": "Running Backtesting…",
}

st.title("Quantum–Classical Market Risk Platform")
st.caption("Monte Carlo VaR / CVaR • Stress Testing • Basel Backtesting")

def api_get(path):
    r = requests.get(f"{API_BASE}{path}")
    r.raise_for_status()
    return r.json()

# Sidebar

st.sidebar.header("Execution Mode")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("⚡ FAST"):
        with st.spinner("Running fast engine..."):
            requests.post(f"{API_BASE}/run", params={"mode": "FAST"})
            st.success("FAST mode run (preview)")

with col2:
    if st.button("🏦 FULL"):
        with st.spinner("Running full engine..."):
            requests.post(f"{API_BASE}/run", params={"mode": "FULL"})
            st.success("FULL mode run (official)")



# Load data
summary = api_get("/results/summary")
figures = api_get("/results/figures")
arrays = api_get("/results/arrays")

# Tabs
tabs = st.tabs([
    "Overview",
    "Distributions",
    "Stress Tests",
    "Risk Limits",
    "Backtesting",
])


from sections.overview import render_overview
from sections.distributions import render_distributions
from sections.backtesting import render_backtesting
from sections.stress import render_stress_tests

with tabs[0]:
    render_overview(summary)

with tabs[1]:
    render_distributions(figures)

with tabs[2]:
    render_stress_tests(figures)

with tabs[3]:
    render_limits(figures)

with tabs[4]:
    render_backtesting(figures)

