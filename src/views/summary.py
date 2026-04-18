"""Page résumé : indicateurs clés de la simulation."""

import streamlit as st

from presentation.components import display_params, require_simulation


st.title("📄 Résumé")

result = require_simulation()
display_params(result)

start_month = result.params.start_month
cashflow_year_idx = 1 if start_month > 1 else 0
cashflow_year_label = cashflow_year_idx + 1
monthly_cashflow = result.cashflow.loc[cashflow_year_idx, "Cashflow (€)"] / 12
net_yield = result.net_yield()
horizon = result.params.resale_horizon

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=f"💰 Cashflow /mois (année {cashflow_year_label})",
        value=f"{monthly_cashflow:.0f} €",
    )

with col2:
    st.metric(label="📈 Rendement Net", value=f"{net_yield:.2f} %")

with col3:
    st.metric(
        label=f"🏦 Enrichissement ({horizon} ans, avant impôts)",
        value=f"{result.wealth_growth:.0f} €",
    )

with col4:
    st.metric(
        label=f"📊 TRI ({horizon} ans, avant impôts)",
        value=f"{result.irr_value:.2f} %",
    )

st.markdown("---")
