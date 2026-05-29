import streamlit as st

def render_backtesting(figures, backtest):
    st.subheader("Rolling Out-of-Sample Backtesting (Basel 99% VaR)")

    # Display Basel Traffic Lights
    col1, col2 = st.columns(2)
    
    q_status = backtest.get("quantum_status", backtest.get("basel_status", "N/A"))
    c_status = backtest.get("classical_status", "N/A")
    
    q_color = "red" if q_status == "RED" else "orange" if q_status == "YELLOW" else "green"
    c_color = "red" if c_status == "RED" else "orange" if c_status == "YELLOW" else "green"
    
    with col1:
        st.markdown(f"### Quantum: :{q_color}[{q_status}]")
        st.caption(f"{backtest['quantum_exceptions']} exceptions / {backtest['total_days']} days")
        
    with col2:
        st.markdown(f"### Classical: :{c_color}[{c_status}]")
        st.caption(f"{backtest['classical_exceptions']} exceptions / {backtest['total_days']} days")
        
    st.markdown("---")

    import os
    for fig in figures["available_figures"]:
        if "backtesting" in fig or "confidence" in fig:
            fig_path = f"figures/{fig}"
            if os.path.exists(fig_path):
                with open(fig_path, "rb") as f:
                    img_bytes = f.read()
                st.image(img_bytes, use_container_width=True)

    st.markdown(
        r"""
        **Basel Backtesting Methodology (99% VaR)**
        - Uses a **250-day rolling window** to forecast next-day 99% VaR.
        - Compares forecasted VaR against **actual realized losses** (out-of-sample).
        - **Green** (0-4 exceptions): Model is well-calibrated.
        - **Yellow** (5-9 exceptions): Model needs review.
        - **Red** (10+ exceptions): Model requires immediate recalibration.
        """
    )
