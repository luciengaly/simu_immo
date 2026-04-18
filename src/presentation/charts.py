"""Constructeurs de figures Plotly pour l'affichage."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from domain.loan import AmortizationEntry
from domain.taxation import TaxationEntry


def build_amortization_chart(
    entries: list[AmortizationEntry], period_label: str
) -> go.Figure:
    """Construit un graphique empilé intérêts / capital d'un emprunt.

    Args:
        entries: Lignes d'amortissement à tracer.
        period_label: Libellé de l'axe temporel ("Mois" ou "Année").

    Returns:
        Figure Plotly prête à l'affichage.
    """
    periods = [e.period for e in entries]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=periods,
            y=[e.interest for e in entries],
            name="Intérêts",
            marker_color="indianred",
        )
    )
    fig.add_trace(
        go.Bar(
            x=periods,
            y=[e.principal for e in entries],
            name="Capital remboursé",
            marker_color="seagreen",
        )
    )
    fig.update_layout(
        barmode="stack",
        title="Répartition du capital restant dû",
        xaxis_title=period_label,
        yaxis_title="Montant (€)",
    )
    return fig


def build_taxation_chart(entries: list[TaxationEntry]) -> go.Figure:
    """Construit le graphique d'optimisation fiscale de la revente.

    Trace le résultat annuel, le déficit reportable et l'amortissement
    reportable, et marque l'année où le déficit s'éteint.

    Args:
        entries: Lignes du tableau fiscal annuel.

    Returns:
        Figure Plotly prête à l'affichage.
    """
    df = pd.DataFrame(
        [
            {
                "Année": e.year,
                "Résultat (€)": e.result,
                "Déficit reportable (€)": e.carry_forward_deficit,
                "Amortissement reportable (€)": e.carry_forward_depreciation,
            }
            for e in entries
        ]
    )
    fig = px.line(
        df,
        x="Année",
        y=[
            "Résultat (€)",
            "Déficit reportable (€)",
            "Amortissement reportable (€)",
        ],
        title="Optimisation fiscale de la revente",
        markers=True,
    )
    zero_deficit = df.loc[df["Déficit reportable (€)"] == 0]
    if not zero_deficit.empty:
        breakeven_year = zero_deficit.iloc[0]["Année"]
        fig.add_vline(
            x=breakeven_year,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Revente Année {breakeven_year:.0f}",
            annotation_position="top left",
        )
    return fig
