"""Page À propos : auteur, technologies et informations diverses."""

import streamlit as st


st.title("ℹ️ À propos")

st.markdown("### 👤 Auteur")
st.markdown(
    """
    **Lucien Galy**
    Développeur et investisseur immobilier amateur.

    Ce simulateur a été conçu pour explorer en toute transparence les
    mécanismes financiers et fiscaux d'un investissement locatif en LMNP
    au régime réel.
    """
)

st.markdown("---")

st.markdown("### 🛠️ Stack technique")
st.markdown(
    """
    - **Python 3** — langage principal
    - **Streamlit** — interface web interactive
    - **Pandas** & **NumPy** — calculs et manipulations de données
    - **numpy-financial** — VAN, TRI, IRR
    - **Architecture** : Clean Architecture (domain / application /
      presentation / infrastructure)
    """
)

st.markdown("---")

st.markdown("### 📐 Méthodologie")
st.markdown(
    """
    - **Amortissement par composants** selon la doctrine fiscale :
      terrain (20 %, non amortissable), gros œuvre (50 % sur 50 ans),
      façades et étanchéités (5 % sur 20 ans), installations générales
      (5 % sur 25 ans), agencements (20 % sur 15 ans).
    - **Mobilier** amorti sur 5 ans.
    - **Résultat fiscal** calculé en 4 étapes réglementaires :
      charges courantes → amortissements de l'année (plafonnés) →
      amortissements reportés → déficits reportés (FIFO, ≤ 10 ans).
    - **TAEG** reconstitué par calcul actuariel (IRR) lorsque le taux
      nominal et l'assurance sont saisis séparément, en intégrant frais
      de dossier et de garantie.
    """
)

st.markdown("---")

st.markdown("### ⚠️ Avertissement")
st.warning(
    "Les résultats produits par ce simulateur sont **indicatifs**. "
    "Ils ne constituent ni un conseil fiscal, ni un conseil "
    "d'investissement. Avant toute décision, consultez un expert-comptable "
    "ou un conseiller en gestion de patrimoine.",
    icon="⚠️",
)

st.markdown("---")

st.caption("Version : développement — Année : 2026")
