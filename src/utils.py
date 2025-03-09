import pandas as pd
import numpy as np
import plotly.graph_objects as go

import pyxirr


import pandas as pd


class Emprunt:
    def __init__(self, montant, duree, taux):
        self.montant = montant
        self.duree = duree * 12
        self.taux = taux / 100 / 12
        self.mensualite = self.calcul_mensualite()

    def calcul_mensualite(self):
        if self.taux > 0:
            return self.montant * self.taux / (1 - (1 + self.taux) ** -self.duree)
        return self.montant / self.duree

    def tableau_amortissement(self):
        capital_restant = self.montant
        tableau = []

        for mois in range(1, self.duree + 1):
            interets = capital_restant * self.taux
            capital_rembourse = self.mensualite - interets
            capital_restant -= capital_rembourse

            tableau.append(
                {
                    "Mois": mois,
                    "Mensualité (€)": round(self.mensualite, 2),
                    "Part intérêts (€)": round(interets, 2),
                    "Part capital (€)": round(capital_rembourse, 2),
                    "Capital restant dû (€)": round(capital_restant, 2),
                }
            )

        return pd.DataFrame(tableau)

    def graphique_amortissement(self, df, periodicite):
        fig_annuel = go.Figure()

        fig_annuel.add_trace(
            go.Bar(
                x=df[periodicite],
                y=df["Part intérêts (€)"],
                name="Intérêts",
                marker_color="indianred",
            )
        )

        fig_annuel.add_trace(
            go.Bar(
                x=df[periodicite],
                y=df["Part capital (€)"],
                name="Capital remboursé",
                marker_color="seagreen",
            )
        )

        fig_annuel.update_layout(
            barmode="stack",
            title="Répartition du capital restant dû",
            xaxis_title=periodicite,
            yaxis_title="Montant (€)",
        )

        return fig_annuel

    def graphique_amortissement_annuel(self, df):
        fig_annuel = self.graphique_amortissement(df, "Année")
        return fig_annuel

    def graphique_amortissement_mensuel(self, df):
        fig_mensuel = self.graphique_amortissement(df, "Mois")
        return fig_mensuel

    def tableau_amortissement_annuel(self):
        tableau = self.tableau_amortissement()
        tableau["Année"] = np.ceil(tableau["Mois"] / 12).astype(int)

        annuel = (
            tableau.groupby("Année")[
                ["Mensualité (€)", "Part intérêts (€)", "Part capital (€)"]
            ]
            .sum()
            .reset_index()
        )

        annuel["Capital restant dû (€)"] = (
            tableau.groupby("Année")["Capital restant dû (€)"].last().values
        )

        return annuel


class SimulationLMNP:
    def __init__(
        self,
        prix_bien,
        frais_notaire,
        travaux,
        meubles,
        apport,
        taux_emprunt,
        duree_emprunt,
        loyer,
        charges,
        aug_loyer,
    ):
        self.prix_bien = prix_bien
        self.frais_notaire = frais_notaire
        self.travaux = travaux
        self.meubles = meubles
        self.apport = apport
        self.taux_emprunt = taux_emprunt
        self.duree_emprunt = duree_emprunt
        self.loyer = loyer
        self.charges = charges
        self.aug_loyer = aug_loyer

        montant_emprunte = (
            prix_bien * (1 + frais_notaire / 100) + travaux + meubles - apport
        )
        self.emprunt = Emprunt(
            montant_emprunte,
            duree_emprunt,
            taux_emprunt,
        )

    def tableau_cashflow(self, duree=10):
        annuite = self.emprunt.mensualite * 12
        loyer_annuel = self.loyer * 12
        cashflow = loyer_annuel - annuite - self.charges
        data = [[1, round(loyer_annuel, 2), round(annuite, 2), round(cashflow, 2)]]
        for annee in range(2, duree + 1):
            loyer_annuel = loyer_annuel * (1 + self.aug_loyer / 100)
            cashflow = loyer_annuel - annuite - self.charges
            data.append(
                [annee, round(loyer_annuel, 2), round(annuite, 2), round(cashflow, 2)]
            )

        return pd.DataFrame(
            data,
            columns=[
                "Année",
                "Revenus (€/an)",
                "Annuité emprunt (€/an)",
                "Cash Flow (€/an)",
            ],
        )

    def rendement_brut(self):
        return (
            self.loyer
            * 12
            / (
                self.prix_bien * (1 + self.frais_notaire / 100)
                + self.travaux
                + self.meubles
            )
            * 100
        )

    def rendement_net(self):
        return (
            (self.loyer * 12 - self.charges)
            / (
                self.prix_bien * (1 + self.frais_notaire / 100)
                + self.travaux
                + self.meubles
            )
            * 100
        )


def initialiser_simulation(
    prix_bien,
    frais_notaire,
    travaux,
    meubles,
    apport,
    taux_emprunt,
    duree_emprunt,
    loyer,
    charges,
    aug_loyer,
):
    return SimulationLMNP(
        prix_bien,
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
