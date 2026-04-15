"""Page résumé : indicateurs clés de la simulation."""

import streamlit as st

from presentation.components import display_params, require_simulation


st.title("📄 Résumé")

result = require_simulation()
display_params(result)

monthly_cashflow = result.cashflow.loc[0, "Cashflow (€)"] / 12
net_yield = result.net_yield()

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="💰 Cashflow /mois", value=f"{monthly_cashflow:.0f} €")

with col2:
    st.metric(label="📈 Rendement Net", value=f"{net_yield:.2f} %")

with col3:
    st.metric(
        label="🏦 Enrichissement (10 ans, avant impôts)",
        value=f"{result.wealth_growth:.0f} €",
    )

with col4:
    st.metric(
        label="📊 TRI (10 ans, avant impôts)",
        value=f"{result.irr_value:.2f} %",
    )

st.markdown("---")
