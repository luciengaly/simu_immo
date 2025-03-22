import streamlit as st

from utils import display_params

st.title("🏷️ Revente")

# Récupérer la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

display_params()

# df = simulation.rendement_patrimonial

# st.dataframe(df, hide_index=True)
