"""Page impôts : tableau fiscal annuel en régime réel."""

import dataclasses

import pandas as pd
import streamlit as st

from application.params import SimulationParams
from application.simulation import LMNPSimulation, SimulationResult
from presentation.components import display_params, require_simulation


TREATMENT_OPTIONS = ["Déduire (charge en année 1)", "Amortir (intégré au bien)"]
TREATMENT_VALUES = {"Déduire (charge en année 1)": "deduction", "Amortir (intégré au bien)": "amortissement"}


@st.cache_data
def _run_simulation(params: SimulationParams) -> SimulationResult:
    """Exécute la simulation complète avec cache Streamlit.

    Args:
        params: Paramètres de simulation (hashables car frozen dataclass).

    Returns:
        Résultat complet de simulation.
    """
    return LMNPSimulation().run(params)


st.title("💰 Impôts")

result = require_simulation()
display_params(result)

st.session_state.setdefault("_acq_fees_treatment_idx", 0)
selected_label = st.radio(
    "Traitement des frais d'acquisition (agence, notaire, courtier)",
    options=TREATMENT_OPTIONS,
    index=st.session_state["_acq_fees_treatment_idx"],
    horizontal=True,
)
st.session_state["_acq_fees_treatment_idx"] = TREATMENT_OPTIONS.index(selected_label)
treatment = TREATMENT_VALUES[selected_label]

if treatment != result.params.acquisition_fees_treatment:
    modified_params = dataclasses.replace(
        result.params, acquisition_fees_treatment=treatment
    )
    result = _run_simulation(modified_params)
    st.session_state.simulation_result = result

taxation_entries = result.taxation_entries

st.markdown(
    """
    Le résultat fiscal est calculé en **4 étapes** par ordre de priorité :
    1. **Charges courantes** (sans plafond) — peut créer un déficit reportable 10 ans
    2. **Amortissements de l'année** (plafonnés) — excédent reportable sans limite
    3. **Amortissements reportés** des années antérieures
    4. **Déficits de charges reportés** (FIFO, ≤ 10 ans)
    """
)

df = pd.DataFrame(
    [
        {
            # Étape 1
            "Année": e.year,
            "Revenus (€)": e.income,
            "Charges courantes (€)": e.current_expenses,
            "Résultat avant amort. (€)": e.result_before_amort,
            # Étape 2
            "Amort. dotation (€)": e.depreciation,
            "Amort. déduit (€)": e.depreciation_used,
            "Stock amorts reportables (€)": e.carry_forward_depreciation,
            # Étape 3
            "Amorts reportés utilisés (€)": e.carry_depreciation_used,
            # Étape 4
            "Déficit ajouté au stock (€)": e.deficit_added,
            "Déficits reportés utilisés (€)": e.deficit_used,
            "Stock déficits reportables (€)": e.carry_forward_deficit,
            # Résultat
            "Résultat fiscal (€)": e.fiscal_result,
            "Imposable micro-BIC (€)": e.taxable_bic,
        }
        for e in taxation_entries
    ]
)

st.write("📋 **Tableau fiscal annuel**")
st.dataframe(df, hide_index=True)
