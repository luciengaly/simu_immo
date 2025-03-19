import pandas as pd
import numpy as np
import plotly.graph_objects as go


class Emprunt:
    def __init__(self, montant, duree, taux):
        self.montant = montant
        self.duree = duree * 12
        self.taux = taux / 12
        self.mensualite = self.calcul_mensualite()
        self.annuite = self.calcul_annuite()
        self.total_mensualites = self.calcul_total_mensualites()
        self.total_interets = self.calcul_total_interets()
        self.tableau_amort_mensuel = self.calcul_tableau_amort_mensuel()
        self.tableau_amort_annuel = self.calcul_tableau_amort_annuel()

    def calcul_total_mensualites(self):
        return self.mensualite * self.duree

    def calcul_total_interets(self):
        return self.total_mensualites - self.montant

    def calcul_annuite(self):
        return self.mensualite * 12

    def calcul_mensualite(self):
        if self.taux > 0:
            return self.montant * self.taux / (1 - (1 + self.taux) ** -self.duree)
        return self.montant / self.duree

    def calcul_tableau_amort_mensuel(self):
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

    def calcul_tableau_amort_annuel(self):
        tableau = self.tableau_amort_mensuel.copy()
        tableau["Année"] = np.ceil(tableau["Mois"] / 12).astype(int)

        annuel = (
            tableau.groupby("Année")[
                ["Mensualité (€)", "Part intérêts (€)", "Part capital (€)"]
            ]
            .sum()
            .reset_index()
        )
        annuel.rename({"Mensualité (€)": "Annuité (€)"}, axis=1, inplace=True)

        annuel["Capital restant dû (€)"] = (
            tableau.groupby("Année")["Capital restant dû (€)"].last().values
        )

        return annuel

    def graphique_amortissement(self, df, periodicite):
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df[periodicite],
                y=df["Part intérêts (€)"],
                name="Intérêts",
                marker_color="indianred",
            )
        )

        fig.add_trace(
            go.Bar(
                x=df[periodicite],
                y=df["Part capital (€)"],
                name="Capital remboursé",
                marker_color="seagreen",
            )
        )

        fig.update_layout(
            barmode="stack",
            title="Répartition du capital restant dû",
            xaxis_title=periodicite,
            yaxis_title="Montant (€)",
        )

        return fig

    def graphique_amort_annuel(self):
        fig = self.graphique_amortissement(self.tableau_amort_annuel, "Année")
        return fig

    def graphique_amort_mensuel(self):
        fig = self.graphique_amortissement(self.tableau_amort_mensuel, "Mois")
        return fig


class Location:
    def __init__(self, loyer, charges, aug_loyer, duree=20):
        self.loyer = loyer
        self.charges = charges
        self.aug_loyer = aug_loyer
        self.duree = duree

        self.bilan_annuel = self.calcul_tableau_bilan_annuel(duree)

    def calcul_tableau_bilan_annuel(self, duree):
        loyer_annuel = self.loyer * 12
        data = [[1, loyer_annuel, self.charges]]
        for annee in range(2, duree + 1):
            loyer_annuel *= 1 + self.aug_loyer
            data.append([annee, loyer_annuel, self.charges])

        return pd.DataFrame(data, columns=["Année", "Revenus (€)", "Dépenses (€)"])


class Amortissement:
    def __init__(
        self, bien, travaux, meubles, duree_bien=20, duree_meubles=8, taux_usure=0.8
    ):
        self.bien = [(bien + travaux) * taux_usure / duree_bien] * duree_bien
        self.meubles = [meubles / duree_meubles] * duree_meubles
        self.total = self.calcul_amort_total()

    def calcul_amort_total(self):
        max_len = max(len(self.bien), len(self.meubles))
        total = []

        for i in range(max_len):
            bien = self.bien[i] if i < len(self.bien) else 0
            meubles = self.meubles[i] if i < len(self.meubles) else 0
            total.append(bien + meubles)

        return total


class Fiscalite:
    def __init__(
        self,
        prix_bien: float,
        frais_agence: float,
        frais_notaire: float,
        travaux: float,
        meubles: float,
        part_interet: list[float],
        revenus: list[float],
        charges: list[float],
    ):
        self.prix_bien = prix_bien
        self.frais_agence = frais_agence
        self.frais_notaire = frais_notaire
        self.travaux = travaux
        self.meubles = meubles
        self.part_interet = part_interet
        self.revenus = revenus
        self.charges = charges

        self.amortissement = Amortissement(prix_bien, travaux, meubles)
        self.deficit_reportable = 0
        self.tableau_impots = self.calcul_impots_regime_reel()

    def calcul_impots_regime_reel(self, duree=20):
        amortissement_reportable = 0
        data = []

        for annee in range(1, duree + 1):
            revenus = self.revenus[annee - 1]
            amortissement = self.amortissement.total[annee - 1]
            charges = self.charges[annee - 1] + self.part_interet[annee - 1]

            if annee == 1:
                charges += self.prix_bien * (self.frais_notaire + self.frais_agence)

            # Calcul du résultat avant déficit reportable et amortissement
            resultat = revenus - charges

            # Gestion du déficit reportable
            if resultat < 0:
                resultat_fiscal = resultat + self.deficit_reportable
                self.deficit_reportable += abs(resultat)
                montant_imposable = 0
                amortissement_reportable += amortissement
            else:
                resultat_fiscal = resultat
                if self.deficit_reportable > 0:
                    compensation = min(resultat_fiscal, self.deficit_reportable)
                    resultat_fiscal -= compensation
                    self.deficit_reportable -= compensation

                # Imputation des amortissements (dans la limite du bénéfice)
                if resultat_fiscal > 0:
                    imputation_amort = min(
                        resultat_fiscal, amortissement + amortissement_reportable
                    )
                    resultat_fiscal -= imputation_amort
                    amortissement_reportable += amortissement - imputation_amort
                else:
                    amortissement_reportable += amortissement

                montant_imposable = max(0, resultat_fiscal)

            data.append(
                [
                    annee,
                    revenus,
                    charges,
                    resultat,
                    resultat_fiscal,
                    self.deficit_reportable,
                    amortissement,
                    amortissement_reportable,
                    montant_imposable,
                ]
            )

        return pd.DataFrame(
            data,
            columns=[
                "Année",
                "Revenus (€)",
                "Charges déductibles (€)",
                "Résultat (€)",
                "Résultat fiscal (€)",
                "Déficit reportable (€)",
                "Amortissement (€)",
                "Amortissement reportable (€)",
                "Montant imposable (€)",
            ],
        )


class SimulationLMNP:
    def __init__(
        self,
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
    ):
        self.prix_bien = prix_bien
        self.frais_agence = frais_agence / 100
        self.frais_notaire = frais_notaire / 100
        self.travaux = travaux
        self.meubles = meubles
        self.apport = apport
        self.taux_emprunt = taux_emprunt / 100
        self.duree_emprunt = duree_emprunt
        self.loyer = loyer
        self.charges = charges
        self.aug_loyer = aug_loyer / 100

        montant_emprunte = (
            prix_bien * (1 + self.frais_agence + self.frais_notaire)
            + travaux
            + meubles
            - apport
        )

        self.emprunt = Emprunt(montant_emprunte, duree_emprunt, self.taux_emprunt)
        self.location = Location(loyer, charges, self.aug_loyer, duree=duree_emprunt)
        self.fiscalite = Fiscalite(
            prix_bien,
            self.frais_agence,
            self.frais_notaire,
            travaux,
            meubles,
            self.emprunt.tableau_amort_annuel["Part intérêts (€)"].values.tolist(),
            self.location.bilan_annuel["Revenus (€)"].values.tolist(),
            self.location.bilan_annuel["Dépenses (€)"].values.tolist(),
        )

    def tableau_cashflow(self, duree=20):
        revenus = self.location.bilan_annuel["Revenus (€)"].values.tolist()
        charges = self.location.bilan_annuel["Dépenses (€)"].values.tolist()
        annuite = self.emprunt.annuite
        part_capital = self.emprunt.tableau_amort_annuel[
            "Part capital (€)"
        ].values.tolist()

        df = pd.DataFrame(
            {
                "Année": range(1, duree + 1),
                "Revenus (€)": revenus,
                "Charges (€)": charges,
                "Annuité (€)": [annuite] * duree,
                "Part capital (€)": part_capital,
            }
        )
        df["Cashflow (€)"] = df["Revenus (€)"] - df["Charges (€)"] - df["Annuité (€)"]
        df["Enrichissement (€)"] = df["Part capital (€)"] + df["Cashflow (€)"]
        return df

    def rendement_brut(self):
        return (
            self.loyer
            * 12
            / (
                self.prix_bien * (1 + self.frais_notaire + self.frais_agence)
                + self.travaux
                + self.meubles
            )
            * 100
        )

    def rendement_net(self):
        return (
            (self.loyer * 12 - self.charges)
            / (
                self.prix_bien * (1 + self.frais_notaire + self.frais_agence)
                + self.travaux
                + self.meubles
            )
            * 100
        )


def initialiser_simulation(
    prix_bien,
    frais_notaire,
    frais_agence,
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
