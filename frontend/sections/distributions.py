import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def render_distributions(figures):
    st.subheader("Risk Distributions")

    import os
    for fig in figures["available_figures"]:
        if "distribution" in fig:
            fig_path = f"figures/{fig}"
            if os.path.exists(fig_path):
                with open(fig_path, "rb") as f:
                    img_bytes = f.read()
                st.image(img_bytes, use_container_width=True)

            
    st.markdown(
        """
        **Distribution Analysis**
        - Comparison of quantum vs classical risk profiles
        - Highlighting tail risks and extreme events
        - Visual assessment of distribution shapes
        """
    )
   
