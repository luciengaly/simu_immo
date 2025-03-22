import streamlit as st
from utils import display_params


st.title("📄 Résumé")

# Récupération de la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

display_params()

cashflow = simulation.tableau_cashflow.loc[0, "Cashflow (€)"] / 12
rendement_net = simulation.rendement_net()
enrichissement = "TODO"
rendement_patrimobial = "TODO"

st.markdown("---")  # Ligne de séparation esthétique
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="💰 Cashflow /mois", value=f"{cashflow:.0f} €")

with col2:
    st.metric(label="📈 Rendement Net", value=f"{rendement_net:.2f} %")

with col3:
    st.metric(label="🏦 Enrichissement", value=enrichissement)

with col4:
    st.metric(label="📊 Rendement Patrimonial", value=rendement_patrimobial)

st.markdown("---")  # Ligne de séparation esthétique
