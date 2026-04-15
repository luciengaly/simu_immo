"""Page revente : VAN, TRI et graphique d'optimisation fiscale."""

import streamlit as st

from presentation.charts import build_taxation_chart
from presentation.components import display_params, require_simulation


st.title("🏷️ Revente")

result = require_simulation()
display_params(result)

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="VAN (10 ans, avant impôts)",
        value=f"{result.npv_value:.0f} €",
    )
with col2:
    st.metric(
        label="TRI (10 ans, avant impôts)",
        value=f"{result.irr_value:.2f} %",
    )

st.plotly_chart(build_taxation_chart(result.taxation_entries))
