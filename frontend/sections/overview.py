import streamlit as st

def render_overview(summary):
    q = summary["portfolio"]["quantum"]
    c = summary["portfolio"]["classical"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Quantum VaR (95%)", f"{q['VaR']*100:.2f}%")
    col2.metric("Quantum CVaR (95%)", f"{q['CVaR']*100:.2f}%")
    col3.metric("Classical VaR (95%)", f"{c['VaR']*100:.2f}%")
    col4.metric("Classical CVaR (95%)", f"{c['CVaR']*100:.2f}%")

    st.markdown("---")
    st.markdown(
        """
        **Methodology**
        - Monte Carlo simulation (quantum vs classical)
        - Identical payoff and aggregation logic
        - Results persisted and audited via batch execution
        """
    )
