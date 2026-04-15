"""Point d'entrée Streamlit : configuration de la navigation multi-pages."""

import streamlit as st


home_pg = st.Page("pages/home.py", title="Accueil")
summary_pg = st.Page("pages/summary.py", title="Résumé")
profitability_pg = st.Page("pages/profitability.py", title="Rentabilité")
loan_pg = st.Page("pages/loan.py", title="Emprunt")
taxes_pg = st.Page("pages/taxes.py", title="Impôts")
resale_pg = st.Page("pages/resale.py", title="Revente")

pg = st.navigation(
    [home_pg, summary_pg, profitability_pg, loan_pg, taxes_pg, resale_pg]
)
st.set_page_config(page_title="🏠 Simulateur LMNP", layout="wide")
pg.run()
