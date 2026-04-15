"""Page d'accueil : formulaire de saisie et lancement de la simulation."""

import streamlit as st

from application.params import SimulationParams
from application.simulation import LMNPSimulation, SimulationResult
from infrastructure.config import load_default_params


DEFAULT_CONFIG_PATH = "./default.yaml"


@st.cache_data
def _run_simulation(params: SimulationParams) -> SimulationResult:
    """Exécute la simulation avec cache Streamlit.

    Args:
        params: Paramètres d'entrée.

    Returns:
        Résultat de simulation.
    """
    return LMNPSimulation().run(params)


def _init_session() -> None:
    """Hydrate la session Streamlit avec les valeurs du YAML par défaut."""
    defaults = load_default_params(DEFAULT_CONFIG_PATH)
    st.session_state.simulation_result = None
    for key, value in defaults.__dict__.items():
        st.session_state[key] = value


st.title("🏠 Accueil")

if "property_price" not in st.session_state:
    _init_session()

with st.form("parameters"):
    st.header("Informations générales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        property_type = st.selectbox("Type de bien", ["Appartement", "Maison"])
        st.header("Achat du bien")
        property_price = st.number_input(
            "Prix d'achat du bien (€, net vendeur)",
            value=st.session_state.property_price,
        )
        agency_fee_rate = st.number_input(
            "Frais d'agence (%)", value=st.session_state.agency_fee_rate
        )
        notary_fee_rate = st.number_input(
            "Frais de notaire (%)", value=st.session_state.notary_fee_rate
        )
        renovation_cost = st.number_input(
            "Montant travaux (€)", value=st.session_state.renovation_cost
        )
        furniture_cost = st.number_input(
            "Montant ameublement (€)", value=st.session_state.furniture_cost
        )

    with col2:
        city = st.text_input("Ville", value=st.session_state.city)
        st.header("Financement")
        down_payment = st.number_input(
            "Apport personnel (€)", value=st.session_state.down_payment
        )
        loan_rate = st.number_input(
            "Taux d'emprunt (%, tout frais inclus)",
            value=st.session_state.loan_rate,
        )
        loan_duration = st.slider(
            "Durée de l'emprunt (années)",
            min_value=5,
            max_value=25,
            step=5,
            value=st.session_state.loan_duration,
        )

    with col3:
        surface = st.number_input("Surface (m²)", value=st.session_state.surface)
        st.header("Location")
        monthly_rent = st.number_input(
            "Loyer mensuel (€)", value=st.session_state.monthly_rent
        )
        annual_expenses = st.number_input(
            "Charges annuelles (€, TF, FC, gestion, assurances PNO-GLI)",
            value=st.session_state.annual_expenses,
        )
        rent_increase_rate = st.number_input(
            "Augmentation annuelle loyer (%)",
            value=st.session_state.rent_increase_rate,
        )

    with col4:
        dpe = st.selectbox("DPE", ["A", "B", "C", "D", "E", "F", "G"])
        st.header("Revente")
        resale = st.number_input(
            "Prix de revente (€, > 100) ou Inflation fixe (%, < 100)",
            value=st.session_state.resale,
        )

    submitted = st.form_submit_button("Enregistrer les paramètres")

if submitted:
    params = SimulationParams(
        property_type=property_type,
        city=city,
        surface=surface,
        dpe=dpe,
        property_price=property_price,
        agency_fee_rate=agency_fee_rate,
        notary_fee_rate=notary_fee_rate,
        renovation_cost=renovation_cost,
        furniture_cost=furniture_cost,
        down_payment=down_payment,
        loan_rate=loan_rate,
        loan_duration=loan_duration,
        monthly_rent=monthly_rent,
        annual_expenses=annual_expenses,
        rent_increase_rate=rent_increase_rate,
        resale=resale,
    )
    for key, value in params.__dict__.items():
        st.session_state[key] = value
    st.session_state.simulation_result = _run_simulation(params)
    st.success(
        "✅ Paramètres enregistrés ! Accédez aux onglets pour voir les résultats."
    )
    st.switch_page("pages/summary.py")
