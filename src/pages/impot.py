import streamlit as st

simulation = st.session_state.get("simulation")

st.title("💰 Impôts")
st.write("Calcul fiscalité et revenus fonciers à implémenter ici.")

df_impots = simulation.calcul_impots_regime_reel(duree=20)
st.write("📋 Tableau d'amortissement annuel")
st.dataframe(df_impots, hide_index=True)
