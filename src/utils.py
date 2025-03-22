import pandas as pd
import numpy as np
from numpy_financial import npv, irr
import plotly.graph_objects as go
import streamlit as st

DUREE_SIMU = 30


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
    def __init__(self, loyer, charges, aug_loyer, duree=30):
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
        self,
        bien,
        travaux,
        meubles,
        duree_bien=25,
        duree_meubles=8,
        taux_usure=0.8,
        duree=30,
    ):
        self.duree = duree
        self.bien = [(bien + travaux) * taux_usure / duree_bien] * duree_bien
        self.meubles = [meubles / duree_meubles] * duree_meubles + [0] * duree
        self.total = self.calcul_amort_total()

    def calcul_amort_total(self):
        bien = (self.bien + [0] * self.duree)[: self.duree]
        meubles = (self.meubles + [0] * self.duree)[: self.duree]
        total = [bien[i] + meubles[i] for i in range(self.duree)]
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
        duree: int = 30,
    ):
        self.prix_bien = prix_bien
        self.frais_agence = frais_agence
        self.frais_notaire = frais_notaire
        self.travaux = travaux
        self.meubles = meubles
        self.part_interet = part_interet
        self.revenus = revenus
        self.charges = charges
        self.duree = duree

        self.amortissement = Amortissement(
            prix_bien, travaux, meubles, duree=self.duree
        )
        self.deficit_reportable = 0
        self.tableau_impots = self.calcul_impots_regime_reel()

    def calcul_impots_regime_reel(self):
        revenus = (self.revenus + [0] * self.duree)[: self.duree]
        charges = (self.charges + [0] * self.duree)[: self.duree]
        part_interets = (self.part_interet + [0] * self.duree)[: self.duree]
        amortissements = (self.amortissement.total + [0] * self.duree)[: self.duree]

        amortissement_reportable = 0
        data = []

        for annee in range(1, self.duree + 1):
            revenu = revenus[annee - 1]
            charge = charges[annee - 1] + part_interets[annee - 1]
            amortissement = amortissements[annee - 1]

            if annee == 1:
                charge += self.prix_bien * (self.frais_notaire + self.frais_agence)

            # Calcul du résultat avant déficit reportable et amortissement
            resultat = revenu - charge

            # Gestion du déficit reportable
            if resultat < 0:
                resultat_fiscal = resultat + self.deficit_reportable
                self.deficit_reportable += abs(resultat)
                montant_imposable_reel = 0
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

                montant_imposable_reel = max(0, resultat_fiscal)

            montant_imposable_bic = revenu * 0.50

            data.append(
                [
                    annee,
                    revenu,
                    charge,
                    resultat,
                    resultat_fiscal,
                    self.deficit_reportable,
                    amortissement,
                    amortissement_reportable,
                    montant_imposable_reel,
                    montant_imposable_bic,
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
                'Montant imposable régime "réel" (€)',
                "Montant imposable régime micro-BIC (€)",
            ],
        )


class SimulationLMNP:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.convert_percent()
        self.cout_total = self.calcul_cout_total()
        self.montant_emprunte = self.calcul_montant_emprunte()

        self.emprunt = Emprunt(
            self.montant_emprunte, self.duree_emprunt, self.taux_emprunt
        )
        self.location = Location(self.loyer, self.charges, self.aug_loyer, DUREE_SIMU)
        self.fiscalite = Fiscalite(
            self.prix_bien,
            self.frais_agence,
            self.frais_notaire,
            self.travaux,
            self.meubles,
            self.emprunt.tableau_amort_annuel["Part intérêts (€)"].values.tolist(),
            self.location.bilan_annuel["Revenus (€)"].values.tolist(),
            self.location.bilan_annuel["Dépenses (€)"].values.tolist(),
            DUREE_SIMU,
        )

        self.tableau_cashflow = self.calcul_tableau_cashflow()
        self.rendement_patrimonial = self.calcul_rendement_patrimonial(
            taux_actualisation=0.08, duree=self.duree_emprunt
        )

    def calcul_revente_nette(self):
        valeurs_revente = []

        prix_net_vendeur = self.prix_bien + self.travaux + self.meubles

        # Cas où self.revente est un pourcentage d'inflation
        if self.revente < 100:
            taux_inflation = self.revente / 100  # Conversion en taux
            for annee in range(1, self.duree_emprunt + 1):
                valeur_annuelle = prix_net_vendeur * ((1 + taux_inflation) ** annee)
                valeurs_revente.append(round(valeur_annuelle, 0))

        return valeurs_revente

    def calcul_montant_emprunte(self):
        return self.cout_total - self.apport

    def calcul_cout_total(self):
        return (
            self.prix_bien * (1 + self.frais_agence + self.frais_notaire)
            + self.travaux
            + self.meubles
        )

    def convert_percent(self):
        self.frais_agence /= 100
        self.frais_notaire /= 100
        self.taux_emprunt /= 100
        self.aug_loyer /= 100

    def calcul_tableau_cashflow(self, duree=30):
        revenus = self.location.bilan_annuel["Revenus (€)"].values.tolist()
        charges = self.location.bilan_annuel["Dépenses (€)"].values.tolist()
        part_capital = self.emprunt.tableau_amort_annuel[
            "Part capital (€)"
        ].values.tolist()
        annuites = self.emprunt.tableau_amort_annuel["Annuité (€)"].values.tolist()

        revenus = (revenus + [0] * duree)[:duree]
        charges = (charges + [0] * duree)[:duree]
        annuites = (annuites + [0] * duree)[:duree]
        part_capital = (part_capital + [0] * duree)[:duree]

        df = pd.DataFrame(
            {
                "Année": range(1, duree + 1),
                "Revenus (€)": revenus,
                "Charges (€)": charges,
                "Annuité (€)": annuites,
                "Part capital (€)": part_capital,
            }
        )
        df["Cashflow (€)"] = df["Revenus (€)"] - df["Charges (€)"] - df["Annuité (€)"]
        df["Enrichissement (€)"] = df["Part capital (€)"] + df["Cashflow (€)"]
        df["Enrichissement cumulé (€)"] = df["Enrichissement (€)"].cumsum()
        return df

    def rendement_brut(self):
        return self.loyer * 12 / self.cout_total * 100

    def rendement_net(self):
        return (self.loyer * 12 - self.charges) / self.cout_total * 100

    def calcul_van(self, taux_actualisation=0.005, duree=20):
        cashflows = self.tableau_cashflow["Cashflow (€)"].values.tolist()
        valeurs_revente = self.calcul_revente_nette()

        van_list = []

        for annee in range(1, duree + 1):
            flux_actualises = cashflows[:annee]
            # print(flux_actualises)
            flux_actualises[-1] += valeurs_revente[annee - 1]
            # print(flux_actualises)
            van = npv(taux_actualisation, [-self.montant_emprunte] + flux_actualises)
            # print([-self.montant_emprunte] + flux_actualises)
            van_list.append(van)

        return van_list

    def calcul_tri(self, duree=20):
        cashflows = self.tableau_cashflow["Cashflow (€)"].values.tolist()
        valeurs_revente = self.calcul_revente_nette()

        tri_list = []

        for annee in range(1, duree + 1):
            flux_actualises = cashflows[:annee]
            flux_actualises[-1] += valeurs_revente[annee - 1]
            tri = (
                irr([-self.montant_emprunte] + flux_actualises) * 100
            )  # Conversion en %
            tri_list.append(tri)

        return tri_list

    def calcul_rendement_patrimonial(self, taux_actualisation=0.005, duree=20):
        annees = list(range(1, duree + 1))
        valeurs_revente = self.calcul_revente_nette()
        van_list = self.calcul_van(taux_actualisation, duree)
        tri_list = self.calcul_tri(duree)

        df = pd.DataFrame(
            {
                "Année": annees,
                "Prix de Revente Net (€)": valeurs_revente[:duree],
                "VAN (€)": van_list,
                "TRI (%)": tri_list,
            }
        )

        return df


@st.cache_data
def launch_simu(**kwargs):
    return SimulationLMNP(**kwargs)


def display_params():
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        # Colonne "Votre Bien"
        with col1:
            st.markdown("🏠 **VOTRE BIEN**")
            cout_total = st.session_state.simulation.cout_total
            surface = st.session_state.surface
            travaux = "Avec travaux" if st.session_state.travaux > 0 else "Sans travaux"
            dpe = st.session_state.dpe
            st.text(
                f"Appartement • Toulouse • {surface}m² • DPE {dpe}\n{cout_total:.0f}€ • {travaux}"
            )

        # Colonne "Location"
        with col2:
            loyer_annuel = st.session_state.simulation.loyer * 12
            charges_annuelles = st.session_state.simulation.charges
            st.markdown("💰 **LOCATION**")
            st.text(
                f"Loyer : {loyer_annuel:.0f}€/an\nCharges : {charges_annuelles:.0f}€/an"
            )

        # Colonne "Crédit"
        with col3:
            apport = st.session_state.apport
            taux = st.session_state.taux_emprunt
            duree = st.session_state.duree_emprunt
            st.markdown("🏦 **CRÉDIT**")
            st.text(f"Taux : {taux:.2f}% • Durée : {duree} ans\nApport : {apport:.0f}€")
