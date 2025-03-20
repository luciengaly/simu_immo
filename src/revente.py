import streamlit as st

from utils import display_params

st.title("🏷️ Revente")

# Récupérer la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

display_params()

st.write("Simulation de la revente et valorisation future.")
