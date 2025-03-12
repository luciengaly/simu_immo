import streamlit as st
import plotly.express as px

st.title("📊 Rentabilité")

# Récupération de la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

# Calcul des indicateurs
rendement_brut = simulation.rendement_brut()
rendement_net = simulation.rendement_net()

# Affichage des métriques (écriture en gros)
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Rendement Brut", value=f"{rendement_brut:.2f} %")

with col2:
    st.metric(label="Rendement Net", value=f"{rendement_net:.2f} %")

st.write(
    """
**Rendement brut** = Loyers annuels / Coût total du projet × 100  
**Rendement net** = (Loyers annuels - charges) / Coût total du projet) × 100
"""
)

df = simulation.tableau_cashflow()

fig = px.line(df, x="Année", y="Cashflow (€)", title="Évolution du Cashflow")
st.plotly_chart(fig)

st.write("### Détail du cashflow annuel")
st.dataframe(df, hide_index=True)
