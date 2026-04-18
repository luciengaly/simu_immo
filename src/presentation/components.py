"""Composants Streamlit réutilisables entre pages."""

import pandas as pd
import streamlit as st

from application.simulation import SimulationResult
from domain.loan import AmortizationEntry


def display_params(result: SimulationResult) -> None:
    """Affiche le bandeau récapitulatif des paramètres en tête de page.

    Args:
        result: Résultat de simulation courant.
    """
    params = result.params
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("🏠 **VOTRE BIEN**")
            renovation_label = (
                "Avec travaux" if params.renovation_cost > 0 else "Sans travaux"
            )
            price_per_m2 = params.property_price / params.surface
            st.text(
                f"{params.property_type} • {params.city} • {params.surface:.0f} m²"
                f" • DPE {params.dpe}\n"
                f"{result.total_cost:.0f} € • {renovation_label}"
                f" • {price_per_m2:.0f} €/m²"
            )

        with col2:
            annual_rent = params.monthly_rent * 12
            st.markdown("💰 **LOCATION**")
            st.text(
                f"Loyer : {annual_rent:.0f} €/an\n"
                f"Charges : {result.resolved_annual_expenses:.0f} €/an"
            )

        with col3:
            st.markdown("🏦 **CRÉDIT**")
            st.text(
                f"Taux : {result.effective_loan_rate:.2f} %"
                f" • Durée : {params.loan_duration} ans\n"
                f"Apport : {params.down_payment:.0f} €"
            )


def require_simulation() -> SimulationResult:
    """Récupère la simulation en session ou stoppe la page avec un avertissement.

    Returns:
        Résultat de simulation courant.
    """
    result = st.session_state.get("simulation_result")
    if not result:
        st.warning(
            "⚠️ Veuillez d'abord définir les paramètres dans l'onglet 'Accueil'."
        )
        st.stop()
    return result


def amortization_to_dataframe(
    entries: list[AmortizationEntry], period_label: str
) -> pd.DataFrame:
    """Convertit un tableau d'amortissement en DataFrame pour ``st.dataframe``.

    Args:
        entries: Lignes d'amortissement.
        period_label: "Mois" ou "Année" — détermine aussi le libellé du remboursement.

    Returns:
        DataFrame formaté (valeurs arrondies à l'euro).
    """
    payment_label = "Mensualité (€)" if period_label == "Mois" else "Annuité (€)"
    return pd.DataFrame(
        [
            {
                period_label: e.period,
                payment_label: round(e.payment, 2),
                "Part intérêts (€)": round(e.interest, 2),
                "Part capital (€)": round(e.principal, 2),
                "Capital restant dû (€)": round(e.remaining_balance, 2),
            }
            for e in entries
        ]
    )
