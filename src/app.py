import streamlit as st

home_pg = st.Page("accueil.py", title="Accueil")
resume_pg = st.Page("resume.py", title="Résumé")
rentabilite_pg = st.Page("rentabilite.py", title="Rentabilité")
emprunt_pg = st.Page("emprunt.py", title="Emprunt")
impots_pg = st.Page("impots.py", title="Impôts")
revente_pg = st.Page("revente.py", title="Revente")
pg = st.navigation(
    [home_pg, resume_pg, rentabilite_pg, emprunt_pg, impots_pg, revente_pg]
)
st.set_page_config(page_title="🏠 Simulateur LMNP", layout="wide")
pg.run()
