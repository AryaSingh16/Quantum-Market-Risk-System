import streamlit as st

def render_stress_tests(figures):
    st.subheader("Stress Tests")

    import os
    for fig in figures["available_figures"]:
        if "stress" in fig:
            fig_path = f"figures/{fig}"
            if os.path.exists(fig_path):
                with open(fig_path, "rb") as f:
                    img_bytes = f.read()
                st.image(img_bytes, use_container_width=True)

    st.markdown(
        """
        **Stress Test Scenarios**
        - Market shocks based on historical events
        - Evaluation of portfolio resilience
        - Comparison of quantum vs classical risk under stress
        """
    )