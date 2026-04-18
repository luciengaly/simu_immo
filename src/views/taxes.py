"""Page impôts : tableau fiscal annuel en régime réel."""

import pandas as pd
import streamlit as st

from presentation.components import display_params, require_simulation


st.title("💰 Impôts")

result = require_simulation()
display_params(result)

df = pd.DataFrame(
    [
        {
            "Année": e.year,
            "Revenus (€)": e.income,
            "Charges déductibles (€)": e.deductible_expenses,
            "Résultat (€)": e.result,
            "Résultat fiscal (€)": e.fiscal_result,
            "Déficit reportable (€)": e.carry_forward_deficit,
            "Amortissement (€)": e.depreciation,
            "Amortissement reportable (€)": e.carry_forward_depreciation,
            'Montant imposable régime "réel" (€)': e.taxable_real,
            "Montant imposable régime micro-BIC (€)": e.taxable_bic,
        }
        for e in result.taxation_entries
    ]
)

st.write("📋 **Tableau fiscal annuel**")
st.dataframe(df, hide_index=True)
