"""Page revente : VAN, TRI et graphique d'optimisation fiscale."""

import streamlit as st

from presentation.charts import build_taxation_chart
from presentation.components import display_params, require_simulation


st.title("🏷️ Revente")

result = require_simulation()
display_params(result)

horizon = result.params.resale_horizon
col1, col2 = st.columns(2)
with col1:
    st.metric(
        label=f"VAN ({horizon} ans, avant impôts)",
        value=f"{result.npv_value:.0f} €",
    )
with col2:
    st.metric(
        label=f"TRI ({horizon} ans, avant impôts)",
        value=f"{result.irr_value:.2f} %",
    )

st.plotly_chart(build_taxation_chart(result.taxation_entries))
