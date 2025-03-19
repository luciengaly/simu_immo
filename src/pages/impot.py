import streamlit as st

# Récupérer la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

st.title("💰 Impôts")

fiscalite = simulation.fiscalite

st.write("📋 Tableau d'amortissement annuel")
st.dataframe(fiscalite.tableau_impots, hide_index=True)
