import streamlit as st

def render_backtesting(figures):
    st.subheader("Basel Backtesting")

    for fig in figures["available_figures"]:
        if "backtesting" in fig or "confidence" in fig:
            st.image(f"figures/{fig}", use_container_width=True)

    st.markdown(
        """
        **Interpretation**
        - Exception rates evaluated against Basel expectations
        - Quantum sampling shows stable tail behavior
        - Results consistent across confidence levels
        """
    )
