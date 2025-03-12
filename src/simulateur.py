import streamlit as st
from utils import initialiser_simulation

st.set_page_config(page_title="Simulateur LMNP", layout="wide")

st.title("🏠 Simulateur LMNP")

if "prix_bien" not in st.session_state:
    st.session_state.prix_bien = 100000
    st.session_state.frais_agence = 6
    st.session_state.frais_notaire = 8
    st.session_state.travaux = 0
    st.session_state.meubles = 3000
    st.session_state.apport = 10000
    st.session_state.taux_emprunt = 3.0
    st.session_state.duree_emprunt = 20
    st.session_state.loyer = 600
    st.session_state.charges = 1500
    st.session_state.aug_loyer = 3.5
    st.session_state.mode_revente = "Valeur d'achat"
    st.session_state.inflation_annuelle = 1
    st.session_state.prix_revente = st.session_state.prix_bien
    st.session_state.annee_revente = 10

# Formulaire de saisie
with st.form("parametres"):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
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
        st.header("Financement")
        apport = st.number_input("Apport personnel (€)", value=st.session_state.apport)
        taux_emprunt = st.number_input(
            "Taux d'emprunt (%, tout frais inclus)", value=st.session_state.taux_emprunt
        )
        duree_emprunt = st.slider(
            "Durée de l'emprunt (années)", 5, 25, st.session_state.duree_emprunt
        )

    with col3:
        st.header("Location")
        loyer = st.number_input("Loyer mensuel (€)", value=st.session_state.loyer)
        charges = st.number_input(
            "Charges annuelles (€, TF, FC, gestion, assurances PNO-GLI)",
            value=st.session_state.charges,
        )
        aug_loyer = st.number_input(
            "Augmentation annuelle loyer (%)", value=st.session_state.aug_loyer
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
    st.session_state.prix_bien = prix_bien
    st.session_state.frais_notaire = frais_notaire
    st.session_state.frais_agence = frais_agence
    st.session_state.travaux = travaux
    st.session_state.meubles = meubles
    st.session_state.apport = apport
    st.session_state.taux_emprunt = taux_emprunt
    st.session_state.duree_emprunt = duree_emprunt
    st.session_state.loyer = loyer
    st.session_state.charges = charges
    st.session_state.aug_loyer = aug_loyer

    st.session_state.simulation = initialiser_simulation(
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
    st.write(st.session_state)
    st.success(
        "✅ Paramètres enregistrés ! Accédez aux onglets pour voir les résultats."
    )
