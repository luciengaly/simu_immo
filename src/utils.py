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

    def annuite(self):
        return self.mensualite * 12

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


class Amortissement:
    def __init__(self, bien, travaux, meubles, duree_bien=20, duree_meubles=10):
        self.amortissement_bien = (bien + travaux) / duree_bien
        self.amortissement_meubles = meubles / duree_meubles

    def total(self):
        return self.amortissement_bien + self.amortissement_meubles


class Location:
    def __init__(self, loyer, charges, aug_loyer):
        self.loyer = loyer
        self.charges = charges
        self.aug_loyer = aug_loyer
        self.loyer_annuel = loyer * 12

    def calcul_loyer_annuel(self, duree):
        loyer_annuel = self.loyer * 12
        data = [[1, loyer_annuel]]
        for annee in range(2, duree + 1):
            loyer_annuel *= 1 + self.aug_loyer / 100
            data.append([annee, loyer_annuel])

        return pd.DataFrame(data, columns=["Année", "Loyer annuel (€)"])


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

        self.emprunt = Emprunt(montant_emprunte, duree_emprunt, taux_emprunt)
        self.amortissement = Amortissement(prix_bien, travaux, meubles)
        self.location = Location(loyer, charges, aug_loyer)

        self.deficit_reportable = 0

    def tableau_cashflow(self, duree=10):
        annuite = self.emprunt.annuite()
        loyer_annuel_df = self.location.calcul_loyer_annuel(duree=20)
        loyer_annuel = loyer_annuel_df.loc[0, "Loyer annuel (€)"]
        cashflow = loyer_annuel - annuite - self.charges
        data = [[1, round(loyer_annuel, 2), round(annuite, 2), round(cashflow, 2)]]
        for annee in range(2, duree + 1):
            loyer_annuel = loyer_annuel_df.loc[annee - 1, "Loyer annuel (€)"]
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

    def calcul_impots_regime_reel(self, duree=10):
        annuite = self.emprunt.annuite()
        amortissement_bien = self.amortissement.amortissement_bien
        amortissement_meubles = self.amortissement.amortissement_meubles
        loyer_annuel_df = self.location.calcul_loyer_annuel(duree=20)
        data = []

        for annee in range(1, duree + 1):
            charges_deductibles = self.charges + annuite
            total_amortissements = amortissement_bien + amortissement_meubles
            charges_totales = charges_deductibles + total_amortissements
            loyer_annuel = loyer_annuel_df.loc[annee - 1, "Loyer annuel (€)"]
            resultat_fiscal = loyer_annuel - charges_totales

            if resultat_fiscal < 0:
                self.deficit_reportable += abs(resultat_fiscal)
                resultat_fiscal = 0
            else:
                if self.deficit_reportable > 0:
                    compensation = min(resultat_fiscal, self.deficit_reportable)
                    resultat_fiscal -= compensation
                    self.deficit_reportable -= compensation

            data.append(
                [
                    annee,
                    round(loyer_annuel, 2),
                    round(charges_deductibles, 2),
                    round(total_amortissements, 2),
                    round(resultat_fiscal, 2),
                    round(self.deficit_reportable, 2),
                ]
            )

        return pd.DataFrame(
            data,
            columns=[
                "Année",
                "Revenus (€/an)",
                "Charges déductibles (€/an)",
                "Amortissements (€/an)",
                "Résultat fiscal (€/an)",
                "Déficit reportable (€/an)",
            ],
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
