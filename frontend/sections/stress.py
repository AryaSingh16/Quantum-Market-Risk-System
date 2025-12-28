import streamlit as st

def render_stress_tests(figures):
    st.subheader("Stress Tests")

    for fig in figures["available_figures"]:
        if "stress" in fig:
            st.image(f"figures/{fig}", use_container_width=True)

    st.markdown(
        """
        **Stress Test Scenarios**
        - Market shocks based on historical events
        - Evaluation of portfolio resilience
        - Comparison of quantum vs classical risk under stress
        """
    )