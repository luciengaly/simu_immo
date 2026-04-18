"""Page rentabilité : rendements et courbes de cashflow."""

import plotly.express as px
import streamlit as st

from presentation.components import display_params, require_simulation


st.title("📊 Rentabilité")

result = require_simulation()
display_params(result)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Rendement Brut", value=f"{result.gross_yield():.2f} %")
with col2:
    st.metric(label="Rendement Net", value=f"{result.net_yield():.2f} %")

df = result.cashflow

st.write("**Détail du cashflow annuel**")
st.dataframe(df, hide_index=True)

st.plotly_chart(
    px.line(
        df,
        x="Année",
        y="Cashflow (€)",
        title="Évolution du Cashflow",
        markers=True,
    )
)

st.plotly_chart(
    px.line(
        df,
        x="Année",
        y="Enrichissement cumulé (€)",
        title="Évolution de l'enrichissement cumulé",
        markers=True,
    )
)
