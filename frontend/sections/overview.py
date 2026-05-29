import streamlit as st
import pandas as pd

def render_overview(summary):
    q = summary["portfolio"]["quantum"]
    c = summary["portfolio"]["classical"]
    tickers = summary.get("tickers", [])

    st.subheader("Portfolio Risk Overview")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Quantum VaR (95%)", f"{q['VaR']*100:.2f}%")
    col2.metric("Quantum CVaR (95%)", f"{q['CVaR']*100:.2f}%")
    col3.metric("Classical VaR (95%)", f"{c['VaR']*100:.2f}%")
    col4.metric("Classical CVaR (95%)", f"{c['CVaR']*100:.2f}%")

    st.markdown("---")
    
    if "MVaR" in q and tickers:
        st.subheader("Risk Attribution (Quantum)")
        
        mvar_data = {
            "Asset": tickers,
            "Marginal VaR (MVaR)": [f"{v*100:.2f}%" for v in q["MVaR"]],
            "Component VaR": [f"{v*100:.2f}%" for v in q["ComponentVaR"]]
        }
        df = pd.DataFrame(mvar_data)
        
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.dataframe(df, hide_index=True)
            
        with col_b:
            # Bar chart of Component VaR
            chart_data = pd.DataFrame({"Asset": tickers, "Component VaR": q["ComponentVaR"]})
            st.bar_chart(chart_data, x="Asset", y="Component VaR", color="#ff4b4b")

    st.markdown(
        """
        **Methodology**
        - Quantum and Classical Monte Carlo path simulation.
        - Cholesky Decomposition mapping for Exact Target Correlation.
        - Results persisted and audited via local SQLite database.
        """
    )
