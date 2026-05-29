import streamlit as st
import requests
from sections.limits import render_limits


API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Quantum-Classical Market Risk",
    layout="wide",
)

st.title("Quantum Monte Carlo Market Risk System")
st.caption(
    "A hybrid quantum-classical portfolio risk engine comparing quantum PQC and classical Monte Carlo scenario generation. "
    "This dashboard presents VaR, CVaR, risk attribution, stress sensitivity, "
    "regulatory backtesting (Basel Traffic Lights), and risk-limit governance."
)


def api_get(path):
    r = requests.get(f"{API_BASE}{path}")
    r.raise_for_status()
    return r.json()

# Sidebar
st.sidebar.header("Execution Mode")
st.sidebar.markdown(
    "**FAST**: 2,000 quantum shots (quick preview)\n\n"
    "**FULL**: 10,000 quantum shots (production accuracy)"
)

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("FAST"):
        with st.spinner("Running fast engine..."):
            requests.post(f"{API_BASE}/run", params={"mode": "FAST"})
            st.success("FAST mode complete")

with col2:
    if st.button("FULL"):
        with st.spinner("Running full engine..."):
            requests.post(f"{API_BASE}/run", params={"mode": "FULL"})
            st.success("FULL mode complete")


# Load data
try:
    summary = api_get("/results/summary")
    figures = api_get("/results/figures")
    arrays = api_get("/results/arrays")
    backtest = api_get("/results/backtest")
except Exception as e:
    st.error(f"Failed to fetch data from API: {e}")
    st.stop()

# Tabs
tabs = st.tabs([
    "Overview & Risk Attribution",
    "Distributions",
    "Stress Tests",
    "Risk Limits",
    "Backtesting",
    "Quantum Theory (QAE)"
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
    render_backtesting(figures, backtest)

with tabs[5]:
    st.subheader("Hybrid Quantum-Classical Architecture & QAE")
    st.markdown(r"""
    ### 1. Parameterized Quantum Circuit (PQC) & Entanglement
    Our quantum engine uses a **Parameterized Quantum Circuit (PQC)** with **CNOT entanglement layers**.
    Unlike a simple uniform Hadamard superposition, this PQC is a tunable ansatz capable of learning
    complex, non-linear dependencies between assets in a portfolio.

    ### 2. Quantum vs Classical Correlation
    - **Classical**: Uses Cholesky Decomposition to map independent standard normal variables to correlated shocks.
    - **Quantum**: The quantum circuit inherently generates dependent shocks via CNOT-induced entanglement.

    ### 3. Hardware Noise Simulation (NISQ Era)
    This platform simulates Noisy Intermediate-Scale Quantum (NISQ) devices using PennyLane's
    `default.mixed` backend with Depolarizing Noise Channels.

    ### 4. Quantum Amplitude Estimation (QAE)
    The ultimate theoretical path to quantum advantage in finance is **Quantum Amplitude Estimation (QAE)**.
    - **Classical Monte Carlo**: Converges at O(1/eps^2) -- to halve sampling error, you need 4x the scenarios.
    - **QAE**: Utilizes the Grover operator to achieve a quadratic speedup O(1/eps).
    - **Why Hybrid?**: Full QAE requires extremely deep circuits currently impossible on NISQ hardware.
      Our hybrid approach uses quantum for scenario generation while classical systems handle aggregation and governance.
    """)
