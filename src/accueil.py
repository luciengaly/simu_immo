import streamlit as st
import yaml
from utils import launch_simu, display_params

DEFAULT_PATH = "./default.yaml"

st.title("🏠 Accueil")


def update_session(dico):
    for key, value in dico.items():
        st.session_state[key] = value


def init_session():
    with open(DEFAULT_PATH, "r") as file:
        default = yaml.safe_load(file)
    st.session_state.simulation = None
    update_session(default)


if "prix_bien" not in st.session_state:
    init_session()

# Formulaire de saisie
with st.form("parametres"):
    st.header("Informations générales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        type = st.selectbox("Type de bien", ["Appartement", "Maison"])
        st.header("Achat du bien")
        prix_bien = st.number_input(
            "Prix d'achat du bien (€, net vendeur)", value=st.session_state.prix_bien
        )
        frais_agence = st.number_input(
            "Frais d'agence (%)", value=st.session_state.frais_agence
        )
        frais_notaire = st.number_input(
            "Frais de notaire (%)", value=st.session_state.frais_notaire
        )
        travaux = st.number_input("Montant travaux (€)", value=st.session_state.travaux)
        meubles = st.number_input(
            "Montant ammeublement (€)", value=st.session_state.meubles
        )

    with col2:
        ville = st.text_input("Ville", value=st.session_state.ville)
        st.header("Financement")
        apport = st.number_input("Apport personnel (€)", value=st.session_state.apport)
        taux_emprunt = st.number_input(
            "Taux d'emprunt (%, tout frais inclus)", value=st.session_state.taux_emprunt
        )
        duree_emprunt = st.slider(
            "Durée de l'emprunt (années)",
            min_value=5,
            max_value=25,
            step=5,
            value=st.session_state.duree_emprunt,
        )

    with col3:
        surface = st.number_input("Surface (m²)", value=st.session_state.surface)
        st.header("Location")
        loyer = st.number_input("Loyer mensuel (€)", value=st.session_state.loyer)
        charges = st.number_input(
            "Charges annuelles (€, TF, FC, gestion, assurances PNO-GLI)",
            value=st.session_state.charges,
        )
        aug_loyer = st.number_input(
            "Augmentation annuelle loyer (%)",
            value=st.session_state.aug_loyer,
        )

    with col4:
        dpe = st.selectbox("DPE", ["A", "B", "C", "D", "E", "F", "G"])
        st.header("Revente")
        revente = st.number_input(
            "Prix de revente (€, > 100) ou Inflation fixe (%, < 100)",
            value=st.session_state.revente,
        )
        st.text("Bientôt disponible")

    submitted = st.form_submit_button("Enregistrer les paramètres")

# Si formulaire validé, on stocke dans la session
if submitted:
    params = {
        "type": type,
        "ville": ville,
        "surface": surface,
        "dpe": dpe,
        "prix_bien": prix_bien,
        "frais_agence": frais_agence,
        "frais_notaire": frais_notaire,
        "travaux": travaux,
        "meubles": meubles,
        "apport": apport,
        "taux_emprunt": taux_emprunt,
        "duree_emprunt": duree_emprunt,
        "loyer": loyer,
        "charges": charges,
        "aug_loyer": aug_loyer,
        "revente": revente,
    }
    update_session(params)
    st.session_state.simulation = launch_simu(**params)

    st.success(
        "✅ Paramètres enregistrés ! Accédez aux onglets pour voir les résultats."
    )
