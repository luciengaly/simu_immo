"""Cas d'usage principal : orchestration complète d'une simulation LMNP."""

from dataclasses import dataclass

import pandas as pd
from numpy_financial import irr, npv

from application.params import SimulationParams
from domain.depreciation import Depreciation
from domain.loan import AmortizationEntry, Loan
from domain.rental import Rental, YearlyRentalFlow
from domain.taxation import Taxation, TaxationEntry


SIMULATION_DURATION_YEARS = 30
DEFAULT_DISCOUNT_RATE = 0.05
DEFAULT_RESALE_HORIZON = 10
RESALE_VALUE_THRESHOLD = 100


@dataclass(frozen=True)
class SimulationResult:
    """Résultats d'une simulation LMNP.

    Attributes:
        params: Paramètres d'entrée utilisés.
        total_cost: Coût total d'acquisition (€).
        loan_amount: Montant emprunté (€).
        loan: Entité emprunt.
        loan_monthly_schedule: Tableau d'amortissement mensuel.
        loan_annual_schedule: Tableau d'amortissement annuel.
        rental_flows: Flux locatifs annuels.
        taxation_entries: Lignes du tableau fiscal annuel.
        cashflow: DataFrame de cashflow annuel (colonnes FR pour affichage).
        npv_value: Valeur actuelle nette sur l'horizon de revente (€).
        irr_value: Taux de rendement interne sur l'horizon de revente (%).
        wealth_growth: Enrichissement cumulé sur l'horizon de revente (€).
    """

    params: SimulationParams
    total_cost: float
    loan_amount: float
    loan: Loan
    loan_monthly_schedule: list[AmortizationEntry]
    loan_annual_schedule: list[AmortizationEntry]
    rental_flows: list[YearlyRentalFlow]
    taxation_entries: list[TaxationEntry]
    cashflow: pd.DataFrame
    npv_value: float
    irr_value: float
    wealth_growth: float

    def gross_yield(self) -> float:
        """Rendement locatif brut (%)."""
        return self.params.monthly_rent * 12 / self.total_cost * 100

    def net_yield(self) -> float:
        """Rendement locatif net de charges (%)."""
        return (
            (self.params.monthly_rent * 12 - self.params.annual_expenses)
            / self.total_cost
            * 100
        )


class LMNPSimulation:
    """Orchestrateur d'une simulation LMNP complète."""

    def __init__(
        self,
        duration_years: int = SIMULATION_DURATION_YEARS,
        discount_rate: float = DEFAULT_DISCOUNT_RATE,
        resale_horizon: int = DEFAULT_RESALE_HORIZON,
    ) -> None:
        """Initialise le cas d'usage.

        Args:
            duration_years: Horizon de projection global (années).
            discount_rate: Taux d'actualisation pour le calcul de VAN (décimal).
            resale_horizon: Année de revente simulée pour VAN/TRI.
        """
        self._duration = duration_years
        self._discount_rate = discount_rate
        self._resale_horizon = resale_horizon

    def run(self, params: SimulationParams) -> SimulationResult:
        """Exécute la simulation complète.

        Args:
            params: Paramètres d'entrée utilisateur.

        Returns:
            Résultat agrégé de la simulation.
        """
        agency_rate = params.agency_fee_rate / 100
        notary_rate = params.notary_fee_rate / 100
        loan_rate = params.loan_rate / 100
        rent_increase = params.rent_increase_rate / 100

        total_cost = self._compute_total_cost(params, agency_rate, notary_rate)
        loan_amount = total_cost - params.down_payment

        loan = Loan(
            amount=loan_amount,
            duration_years=params.loan_duration,
            annual_rate=loan_rate,
        )
        monthly_schedule = loan.monthly_schedule()
        annual_schedule = loan.annual_schedule()

        rental = Rental(
            monthly_rent=params.monthly_rent,
            annual_expenses=params.annual_expenses,
            rent_increase_rate=rent_increase,
        )
        rental_flows = rental.projected_flows(self._duration)

        depreciation = Depreciation(
            property_value=params.property_price,
            renovation_cost=params.renovation_cost,
            furniture_cost=params.furniture_cost,
        )
        depreciation_schedule = depreciation.annual_schedule(self._duration)

        taxation = Taxation(
            property_value=params.property_price,
            agency_fee_rate=agency_rate,
            notary_fee_rate=notary_rate,
        )
        loan_interests = self._pad_to_duration(
            [e.interest for e in annual_schedule]
        )
        taxation_entries = taxation.compute(
            incomes=[f.income for f in rental_flows],
            expenses=[f.expenses for f in rental_flows],
            loan_interests=loan_interests,
            depreciations=depreciation_schedule,
        )

        cashflow_df = self._build_cashflow_frame(rental_flows, annual_schedule)

        resale_value = self._compute_resale_value(params)
        remaining_balance = annual_schedule[
            min(self._resale_horizon, len(annual_schedule)) - 1
        ].remaining_balance
        discounted_flows = self._build_discounted_flows(
            cashflow_df["Cashflow (€)"].tolist(),
            params.down_payment,
            resale_value,
            remaining_balance,
        )

        return SimulationResult(
            params=params,
            total_cost=total_cost,
            loan_amount=loan_amount,
            loan=loan,
            loan_monthly_schedule=monthly_schedule,
            loan_annual_schedule=annual_schedule,
            rental_flows=rental_flows,
            taxation_entries=taxation_entries,
            cashflow=cashflow_df,
            npv_value=float(npv(self._discount_rate, discounted_flows)),
            irr_value=float(irr(discounted_flows) * 100),
            wealth_growth=sum(discounted_flows),
        )

    def _compute_total_cost(
        self,
        params: SimulationParams,
        agency_rate: float,
        notary_rate: float,
    ) -> float:
        """Coût total d'acquisition (prix + frais + travaux + mobilier)."""
        return (
            params.property_price * (1 + agency_rate + notary_rate)
            + params.renovation_cost
            + params.furniture_cost
        )

    def _pad_to_duration(self, values: list[float]) -> list[float]:
        """Aligne une liste sur la durée de simulation en complétant par des zéros."""
        return (values + [0.0] * self._duration)[: self._duration]

    def _build_cashflow_frame(
        self,
        rental_flows: list[YearlyRentalFlow],
        annual_schedule: list[AmortizationEntry],
    ) -> pd.DataFrame:
        """Construit le DataFrame de cashflow annuel.

        Args:
            rental_flows: Flux locatifs annuels.
            annual_schedule: Tableau d'amortissement annuel de l'emprunt.

        Returns:
            DataFrame avec colonnes FR prêtes pour l'affichage.
        """
        incomes = self._pad_to_duration([f.income for f in rental_flows])
        expenses = self._pad_to_duration([f.expenses for f in rental_flows])
        annuities = self._pad_to_duration([e.payment for e in annual_schedule])
        principals = self._pad_to_duration([e.principal for e in annual_schedule])

        df = pd.DataFrame(
            {
                "Année": range(1, self._duration + 1),
                "Revenus (€)": incomes,
                "Charges (€)": expenses,
                "Annuité (€)": annuities,
                "Part capital (€)": principals,
            }
        )
        df["Cashflow (€)"] = (
            df["Revenus (€)"] - df["Charges (€)"] - df["Annuité (€)"]
        )
        df["Enrichissement (€)"] = df["Part capital (€)"] + df["Cashflow (€)"]
        df["Enrichissement cumulé (€)"] = df["Enrichissement (€)"].cumsum()
        return df

    def _compute_resale_value(self, params: SimulationParams) -> float:
        """Calcule la valeur de revente à l'horizon configuré.

        Interprète ``params.resale`` selon sa magnitude : en dessous du seuil
        c'est un taux d'inflation annuel appliqué au prix net vendeur, au-dessus
        c'est directement le prix de revente.
        """
        if params.resale < RESALE_VALUE_THRESHOLD:
            inflation_rate = params.resale / 100
            net_price = (
                params.property_price
                + params.renovation_cost
                + params.furniture_cost
            )
            return round(net_price * (1 + inflation_rate) ** self._resale_horizon)
        return params.resale

    def _build_discounted_flows(
        self,
        cashflows: list[float],
        down_payment: float,
        resale_value: float,
        remaining_balance: float,
    ) -> list[float]:
        """Construit la série de flux utilisée pour VAN et TRI.

        Ajoute l'apport négatif en année 1 et le solde de revente (prix de
        revente moins capital restant dû) à l'horizon.
        """
        flows = list(cashflows[: self._resale_horizon])
        flows[0] -= down_payment
        flows[-1] += resale_value - remaining_balance
        return flows
