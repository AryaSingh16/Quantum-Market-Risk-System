import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def render_distributions(figures):
    st.subheader("Risk Distributions")

    for fig in figures["available_figures"]:
        if "distribution" in fig:
            st.image(f"figures/{fig}", use_container_width=True)

            
    st.markdown(
        """
        **Distribution Analysis**
        - Comparison of quantum vs classical risk profiles
        - Highlighting tail risks and extreme events
        - Visual assessment of distribution shapes
        """
    )
   
