import streamlit as st
import plotly.express as px

st.title("🏦 Emprunt")

# Récupérer la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

emprunt = simulation.emprunt

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Montant emprunté", value=f"{emprunt.montant:,.0f} €")

with col2:
    st.metric(label="Total à rembourser", value=f"{emprunt.total_mensualites:,.0f} €")

with col3:
    st.metric(label="Intérêts totaux", value=f"{emprunt.total_interets:,.0f} €")

# Création des onglets
tab_annuel, tab_mensuel = st.tabs(["📊 Annuel", "📆 Mensuel"])

### Onglet Annuel ###
with tab_annuel:
    fig_annuel = emprunt.graphique_amort_annuel()

    st.plotly_chart(fig_annuel)

    # Affichage du tableau d'amortissement annuel
    st.write("📋 Tableau d'amortissement annuel")
    st.dataframe(emprunt.tableau_amort_annuel, hide_index=True)

### Onglet Mensuel ###
with tab_mensuel:
    fig_mensuel = emprunt.graphique_amort_mensuel()

    st.plotly_chart(fig_mensuel)

    # Affichage du tableau d'amortissement mensuel
    st.write("📋 Tableau d'amortissement mensuel")
    st.dataframe(emprunt.tableau_amort_mensuel, hide_index=True)
