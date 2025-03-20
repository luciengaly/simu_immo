import streamlit as st
import yaml
from utils import launch_simu

DEFAULT_PATH = "./src/default.yaml"

st.title("🏠 Accueil")


@st.cache_data
def init_session():
    with open(DEFAULT_PATH, "r") as file:
        default = yaml.safe_load(file)
    return default


default = init_session()

# Formulaire de saisie
with st.form("parametres"):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.header("Achat du bien")
        prix_bien = st.number_input(
            "Prix d'achat du bien (€, net vendeur)",
            key="prix_bien",
            value=default["prix_bien"],
        )
        frais_agence = st.number_input(
            "Frais d'agence (%)",
            key="frais_agence",
            value=default["frais_agence"],
        )
        frais_notaire = st.number_input(
            "Frais de notaire (%)",
            key="frais_notaire",
            value=default["frais_notaire"],
        )
        travaux = st.number_input(
            "Montant travaux (€)", key="travaux", value=default["travaux"]
        )
        meubles = st.number_input(
            "Montant ammeublement (€)", key="meubles", value=default["meubles"]
        )

    with col2:
        st.header("Financement")
        apport = st.number_input(
            "Apport personnel (€)", key="apport", value=default["apport"]
        )
        taux_emprunt = st.number_input(
            "Taux d'emprunt (%, tout frais inclus)",
            key="taux_emprunt",
            value=default["taux_emprunt"],
        )
        duree_emprunt = st.slider(
            "Durée de l'emprunt (années)",
            5,
            25,
            key="duree_emprunt",
            value=default["duree_emprunt"],
        )

    with col3:
        st.header("Location")
        loyer = st.number_input(
            "Loyer mensuel (€)", key="loyer", value=default["loyer"]
        )
        charges = st.number_input(
            "Charges annuelles (€, TF, FC, gestion, assurances PNO-GLI)",
            key="charges",
            value=default["charges"],
        )
        aug_loyer = st.number_input(
            "Augmentation annuelle loyer (%)",
            key="aug_loyer",
            value=default["aug_loyer"],
        )

    with col4:
        st.header("Impôts")
        st.write(
            "Les impôts sont calculés sur la base du régime réel, sans prise en compte du micro-BIC."
        )

    with col5:
        st.header("Revente")

    submitted = st.form_submit_button("Enregistrer les paramètres")

# Si formulaire validé, on stocke dans la session
if submitted:
    st.session_state.simulation = launch_simu(
        prix_bien,
        frais_agence,
        frais_notaire,
        travaux,
        meubles,
        apport,
        taux_emprunt,
        duree_emprunt,
        loyer,
        charges,
        aug_loyer,
    )
    st.success(
        "✅ Paramètres enregistrés ! Accédez aux onglets pour voir les résultats."
    )
