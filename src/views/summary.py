"""Page résumé : indicateurs clés de la simulation."""

import streamlit as st

from presentation.components import display_params, require_simulation


def _fmt_eur(value: float) -> str:
    """Formate un montant en euros avec séparateur de milliers espace.

    Args:
        value: Montant en euros.

    Returns:
        Chaîne formatée (ex: ``"125 000 €"``).
    """
    return f"{value:,.0f} €".replace(",", " ")


def _fmt_pct(value: float) -> str:
    """Formate un pourcentage avec 2 décimales.

    Args:
        value: Pourcentage (ex: 3.45).

    Returns:
        Chaîne formatée (ex: ``"3.45 %"``).
    """
    return f"{value:.2f} %"


st.title("📄 Résumé")

result = require_simulation()
display_params(result)

params = result.params
start_month = params.start_month
cashflow_year_idx = 1 if start_month > 1 else 0
monthly_cashflow = result.cashflow.loc[cashflow_year_idx, "Cashflow (€)"] / 12
monthly_payment = result.loan_monthly_schedule[0].payment
horizon = params.resale_horizon

st.markdown("---")
st.markdown("### 🏠 Investissement")
col1, col2, col3 = st.columns(3)
col1.metric("Coût total", _fmt_eur(result.total_cost))
col2.metric("Apport", _fmt_eur(params.down_payment))
col3.metric("Montant du prêt", _fmt_eur(result.loan_amount))

st.markdown("### 🏦 Prêt")
col1, col2, col3 = st.columns(3)
col1.metric("TAEG", _fmt_pct(result.effective_taeg()))
col2.metric("Durée", f"{params.loan_duration} ans")
col3.metric("Mensualités de prêt", _fmt_eur(monthly_payment))

st.markdown("### 💰 Exploitation")
col1, col2, col3 = st.columns(3)
col1.metric("Loyer / mois", _fmt_eur(params.monthly_rent))
col2.metric("Charges / mois", _fmt_eur(result.resolved_annual_expenses / 12))
col3.metric("Trésorerie mensuelle", _fmt_eur(monthly_cashflow))

st.markdown("### 📈 Rendements")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net de frais d'acquisition", _fmt_pct(result.gross_yield()))
col2.metric("Net de charges d'exploitation", _fmt_pct(result.net_yield()))
col3.metric(f"Gain net à {horizon} ans*", _fmt_eur(result.wealth_growth))
col4.metric(f"TRI {horizon} ans*", _fmt_pct(result.irr_value))

st.caption("*avant impôts")
