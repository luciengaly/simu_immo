"""Page d'accueil : formulaire de saisie et lancement de la simulation."""

import streamlit as st

from application.params import SimulationParams
from application.simulation import LMNPSimulation, SimulationResult
from infrastructure.config import load_default_params


DEFAULT_CONFIG_PATH = "./default.yaml"
PERIODS = ["mensuel", "trimestriel", "annuel"]
MONTHS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


@st.cache_data
def _run_simulation(params: SimulationParams) -> SimulationResult:
    """Exécute la simulation avec cache Streamlit.

    Args:
        params: Paramètres d'entrée.

    Returns:
        Résultat de simulation.
    """
    return LMNPSimulation().run(params)


LOAN_RATE_OPTIONS = ["TAEG (tout frais inclus)", "Taux nominal + Assurance (TAEA)"]
EXPENSE_OPTIONS = ["Global (total annuel)", "Détaillé par poste"]


def _init_session() -> None:
    """Hydrate la session Streamlit avec les valeurs du YAML par défaut."""
    defaults = load_default_params(DEFAULT_CONFIG_PATH)
    st.session_state.simulation_result = None
    for key, value in defaults.__dict__.items():
        st.session_state[key] = value
    # Modes de saisie — clés persistantes non liées à un widget,
    # Streamlit ne les supprime pas lors des navigations entre pages.
    st.session_state.setdefault("_loan_rate_mode_idx", 0)
    st.session_state.setdefault("_expense_mode_idx", 0)


def _expense_row(
    label: str,
    amount_key: str,
    period_key: str,
    default_period: str,
) -> tuple[float, str]:
    """Affiche une ligne de charge avec montant et périodicité.

    Args:
        label: Libellé du poste de charge.
        amount_key: Clé session pour le montant.
        period_key: Clé session pour la périodicité.
        default_period: Périodicité par défaut.

    Returns:
        Tuple (montant, périodicité).
    """
    col_a, col_b = st.columns([3, 2])
    with col_a:
        amount = st.number_input(
            label,
            value=float(st.session_state.get(amount_key, 0.0)),
            min_value=0.0,
            key=f"_w_{amount_key}",
        )
    with col_b:
        period = st.selectbox(
            "Périodicité",
            options=PERIODS,
            index=PERIODS.index(st.session_state.get(period_key, default_period)),
            label_visibility="collapsed",
            key=f"_w_{period_key}",
        )
    return amount, period


st.title("🏠 Accueil")

if "property_price" not in st.session_state:
    _init_session()

st.session_state.setdefault("_loan_rate_mode_idx", 0)
st.session_state.setdefault("_expense_mode_idx", 0)

col_mode1, col_mode2 = st.columns(2)
with col_mode1:
    loan_rate_mode = st.radio(
        "Mode de saisie du taux d'emprunt",
        options=LOAN_RATE_OPTIONS,
        index=st.session_state["_loan_rate_mode_idx"],
        horizontal=True,
    )
    st.session_state["_loan_rate_mode_idx"] = LOAN_RATE_OPTIONS.index(loan_rate_mode)
with col_mode2:
    expense_mode = st.radio(
        "Mode de saisie des charges",
        options=EXPENSE_OPTIONS,
        index=st.session_state["_expense_mode_idx"],
        horizontal=True,
    )
    st.session_state["_expense_mode_idx"] = EXPENSE_OPTIONS.index(expense_mode)

with st.form("parameters"):
    st.header("Informations générales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        property_type = st.selectbox("Type de bien", ["Appartement", "Maison"])
        start_month_idx = int(st.session_state.get("start_month", 1)) - 1
        selected_month = st.selectbox(
            "Mois de début d'activité",
            options=MONTHS,
            index=start_month_idx,
        )
        start_month = MONTHS.index(selected_month) + 1
        st.header("Achat du bien")
        property_price = st.number_input(
            "Prix d'achat du bien (€, net vendeur)",
            value=st.session_state.property_price,
        )
        agency_fee_rate = st.number_input(
            "Frais d'agence (% si < 100, sinon €)",
            value=st.session_state.agency_fee_rate,
        )
        notary_fee_rate = st.number_input(
            "Frais d'acte notaire (% si < 100, sinon €)",
            value=st.session_state.notary_fee_rate,
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
        use_nominal = loan_rate_mode == "Taux nominal + Assurance (TAEA)"
        if use_nominal:
            loan_rate = 0.0
            loan_nominal_rate = st.number_input(
                "Taux nominal (%)",
                value=float(st.session_state.get("loan_nominal_rate", 0.0)),
                min_value=0.0,
            )
            loan_insurance_rate = st.number_input(
                "Taux assurance TAEA (%)",
                value=float(st.session_state.get("loan_insurance_rate", 0.0)),
                min_value=0.0,
            )
        else:
            loan_rate = st.number_input(
                "TAEG (%, tout frais inclus)",
                value=st.session_state.loan_rate,
            )
            loan_nominal_rate = 0.0
            loan_insurance_rate = 0.0
        loan_duration = st.slider(
            "Durée de l'emprunt (années)",
            min_value=5,
            max_value=25,
            step=5,
            value=st.session_state.loan_duration,
        )
        guarantee_fee = st.number_input(
            "Frais de garantie (€, optionnel)",
            value=float(st.session_state.get("guarantee_fee", 0.0)),
            min_value=0.0,
        )
        dossier_fee = st.number_input(
            "Frais de dossier (€, optionnel)",
            value=float(st.session_state.get("dossier_fee", 0.0)),
            min_value=0.0,
        )
        death_insurance_monthly = st.number_input(
            "Assurance décès (€/mois, optionnel)",
            value=float(st.session_state.get("death_insurance_monthly", 0.0)),
            min_value=0.0,
        )

    with col3:
        surface = st.number_input("Surface (m²)", value=st.session_state.surface)
        st.header("Location")
        monthly_rent = st.number_input(
            "Loyer mensuel (€)", value=st.session_state.monthly_rent
        )
        use_detailed = expense_mode == "Détaillé par poste"
        if use_detailed:
            annual_expenses = 0.0
            st.caption("Montant — Périodicité")
            pno_insurance, pno_period = _expense_row(
                "Assurance PNO (€)", "pno_insurance", "pno_period", "mensuel"
            )
            gli_insurance, gli_period = _expense_row(
                "Assurance GLI (€)", "gli_insurance", "gli_period", "mensuel"
            )
            agency_management_fee, agency_management_fee_period = _expense_row(
                "Honoraires agence gestion (€)",
                "agency_management_fee",
                "agency_management_fee_period",
                "mensuel",
            )
            property_tax, property_tax_period = _expense_row(
                "Taxe foncière (€)", "property_tax", "property_tax_period", "annuel"
            )
            condo_fees, condo_fees_period = _expense_row(
                "Charges de copro (€)", "condo_fees", "condo_fees_period", "trimestriel"
            )
            accounting_fee, accounting_fee_period = _expense_row(
                "Frais de comptabilité (€)",
                "accounting_fee",
                "accounting_fee_period",
                "annuel",
            )
        else:
            annual_expenses = st.number_input(
                "Charges annuelles (€, TF, copro, gestion, assurances)",
                value=st.session_state.annual_expenses,
            )
            pno_insurance = pno_period = 0.0
            gli_insurance = gli_period = 0.0
            agency_management_fee = agency_management_fee_period = 0.0
            property_tax = property_tax_period = 0.0
            condo_fees = condo_fees_period = 0.0
            accounting_fee = accounting_fee_period = 0.0
            pno_period = "mensuel"
            gli_period = "mensuel"
            agency_management_fee_period = "mensuel"
            property_tax_period = "annuel"
            condo_fees_period = "trimestriel"
            accounting_fee_period = "annuel"
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
        resale_horizon = st.slider(
            "Horizon de revente (années)",
            min_value=1,
            max_value=30,
            value=int(st.session_state.get("resale_horizon", 10)),
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
        loan_nominal_rate=loan_nominal_rate,
        loan_insurance_rate=loan_insurance_rate,
        guarantee_fee=guarantee_fee,
        dossier_fee=dossier_fee,
        pno_insurance=pno_insurance,
        pno_period=pno_period,
        gli_insurance=gli_insurance,
        gli_period=gli_period,
        agency_management_fee=agency_management_fee,
        agency_management_fee_period=agency_management_fee_period,
        property_tax=property_tax,
        property_tax_period=property_tax_period,
        condo_fees=condo_fees,
        condo_fees_period=condo_fees_period,
        accounting_fee=accounting_fee,
        accounting_fee_period=accounting_fee_period,
        death_insurance_monthly=death_insurance_monthly,
        resale_horizon=resale_horizon,
        start_month=start_month,
    )
    for key, value in params.__dict__.items():
        st.session_state[key] = value
    st.session_state.simulation_result = _run_simulation(params)
    st.success(
        "✅ Paramètres enregistrés ! Accédez aux onglets pour voir les résultats."
    )
    st.switch_page("views/summary.py")
