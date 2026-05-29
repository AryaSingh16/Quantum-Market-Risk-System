import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"


def render_limits(figures):
    r = requests.get(f"{API_BASE}/results/limits")
    r.raise_for_status()
    limits = r.json()

    st.subheader("Daily Risk Limits")

    for metric, status in limits.items():
        if status == "PASS":
            st.success(f"{metric}: {status}")
        elif status == "WARNING":
            st.warning(f"{metric}: {status}")
        else:
            st.error(f"{metric}: {status}")

    st.subheader("Plots")

    import os
    for fig in figures["available_figures"]:
        if "risk_limits" in fig:
            fig_path = f"figures/{fig}"
            if os.path.exists(fig_path):
                with open(fig_path, "rb") as f:
                    img_bytes = f.read()
                st.image(img_bytes, use_container_width=True)
    
    
    st.markdown(
        """
        **Governance Notes**
        - PASS: within approved limits  
        - WARNING: elevated risk, monitoring required  
        - BREACH: escalation required  
        """
    )

