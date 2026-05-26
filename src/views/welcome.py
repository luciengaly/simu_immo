"""Page d'accueil : présentation du simulateur LMNP."""

import streamlit as st


st.title("🏠 Simulateur LMNP")

st.markdown(
    """
    Bienvenue sur le **simulateur d'investissement locatif en LMNP**
    (Location Meublée Non Professionnelle, régime réel).

    Cet outil vous permet de modéliser un projet d'achat immobilier en
    location meublée et d'en évaluer la rentabilité, la fiscalité et la
    plus-value à la revente.
    """
)

st.markdown("---")

st.markdown("### ✨ Fonctionnalités")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        **📊 Rentabilité**
        - Rendement brut et net
        - Cashflow annuel et mensuel
        - Enrichissement cumulé

        **🏦 Emprunt**
        - TAEG ou taux nominal + assurance
        - Frais de dossier, garantie, courtage
        - Tableau d'amortissement mensuel et annuel
        """
    )

with col2:
    st.markdown(
        """
        **💰 Fiscalité LMNP (régime réel)**
        - Amortissement par composants (gros œuvre, façades, etc.)
        - Déficits de charges reportables (10 ans)
        - Amortissements reportables (sans limite)
        - Choix : déduction ou amortissement des frais d'acquisition

        **📈 Revente**
        - VAN, TRI sur horizon configurable
        - Prix fixe ou évolution par inflation
        """
    )

st.markdown("---")

st.markdown("### 🚀 Pour commencer")
st.markdown(
    """
    1. Ouvrez l'onglet **Paramètres** dans la barre latérale.
    2. Renseignez les caractéristiques du bien, du financement, de la
       location et de la revente.
    3. Cliquez sur **Enregistrer les paramètres**.
    4. Explorez les onglets **Résumé**, **Rentabilité**, **Emprunt**,
       **Impôts** et **Revente** pour analyser votre projet.
    """
)

st.info(
    "💡 Les calculs sont indicatifs et ne constituent pas un conseil "
    "fiscal ou financier. Consultez un expert-comptable ou un conseiller "
    "en gestion de patrimoine avant tout engagement.",
    icon="ℹ️",
)
