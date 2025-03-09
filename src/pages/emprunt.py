import streamlit as st
import plotly.express as px

st.title("🏦 Emprunt")

# Récupérer la simulation depuis la session
simulation = st.session_state.get("simulation")
if not simulation:
    st.warning("⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'.")
    st.stop()

emprunt = simulation.emprunt

total_mensualites = emprunt.mensualite * emprunt.duree
total_interets = total_mensualites - emprunt.montant

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Montant emprunté", value=f"{emprunt.montant:,.0f} €")

with col2:
    st.metric(label="Total à rembourser", value=f"{total_mensualites:,.0f} €")

with col3:
    st.metric(label="Intérêts totaux", value=f"{total_interets:,.0f} €")

# Création des onglets
tab_annuel, tab_mensuel = st.tabs(["📊 Annuel", "📆 Mensuel"])

### Onglet Annuel ###
with tab_annuel:
    df_annuel = emprunt.tableau_amortissement_annuel()
    fig_annuel = emprunt.graphique_amortissement_annuel(df_annuel)

    st.plotly_chart(fig_annuel)

    # Affichage du tableau d'amortissement annuel
    st.write("📋 Tableau d'amortissement annuel")
    st.dataframe(df_annuel, hide_index=True)

### Onglet Mensuel ###
with tab_mensuel:
    df_mensuel = emprunt.tableau_amortissement()
    fig_mensuel = emprunt.graphique_amortissement_mensuel(df_mensuel)

    st.plotly_chart(fig_mensuel)

    # Affichage du tableau d'amortissement mensuel
    st.write("📋 Tableau d'amortissement mensuel")
    st.dataframe(df_mensuel, hide_index=True)
