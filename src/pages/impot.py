import streamlit as st

simulation = st.session_state.get("simulation")

st.title("💰 Impôts")

fiscalite = simulation.fiscalite

st.write("📋 Tableau d'amortissement annuel")
st.dataframe(fiscalite.tableau_impots, hide_index=True)
