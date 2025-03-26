import streamlit as st

from utils import display_params

st.title("🏷️ Revente")

# Récupérer la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

display_params()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="VAN (10 ans, avant impôts)", value=f"{simulation.van:.0f} €")

with col2:
    st.metric(label="TRI (10 ans, avant impôts)", value=f"{simulation.tri:.2f} %")
