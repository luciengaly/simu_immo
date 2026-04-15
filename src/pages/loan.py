"""Page emprunt : indicateurs et tableaux d'amortissement."""

import streamlit as st

from presentation.charts import build_amortization_chart
from presentation.components import (
    amortization_to_dataframe,
    display_params,
    require_simulation,
)


st.title("🏦 Emprunt")

result = require_simulation()
display_params(result)

loan = result.loan

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Montant emprunté", value=f"{loan.amount:,.0f} €")
with col2:
    st.metric(label="Total à rembourser", value=f"{loan.total_payments:,.0f} €")
with col3:
    st.metric(label="Intérêts totaux", value=f"{loan.total_interest:,.0f} €")

tab_annual, tab_monthly = st.tabs(["📊 Annuel", "📆 Mensuel"])

with tab_annual:
    st.plotly_chart(build_amortization_chart(result.loan_annual_schedule, "Année"))
    st.write("📋 **Tableau d'amortissement annuel**")
    st.dataframe(
        amortization_to_dataframe(result.loan_annual_schedule, "Année"),
        hide_index=True,
    )

with tab_monthly:
    st.plotly_chart(build_amortization_chart(result.loan_monthly_schedule, "Mois"))
    st.write("📋 **Tableau d'amortissement mensuel**")
    st.dataframe(
        amortization_to_dataframe(result.loan_monthly_schedule, "Mois"),
        hide_index=True,
    )
