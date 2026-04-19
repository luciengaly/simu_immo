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
FEE_AMOUNT_THRESHOLD = 100
PERIOD_MULTIPLIERS: dict[str, int] = {
    "mensuel": 12,
    "trimestriel": 4,
    "annuel": 1,
}


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
        effective_loan_rate: Taux effectif annuel utilisé pour le calcul (%).
        resolved_annual_expenses: Charges annuelles effectives utilisées (€).
        resolved_death_insurance_annual: Coût annuel assurance décès (€).
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
    effective_loan_rate: float
    resolved_annual_expenses: float
    resolved_death_insurance_annual: float

    def gross_yield(self) -> float:
        """Rendement locatif brut (%)."""
        return self.params.monthly_rent * 12 / self.total_cost * 100

    def net_yield(self) -> float:
        """Rendement locatif net de charges (%)."""
        return (
            (self.params.monthly_rent * 12 - self.resolved_annual_expenses)
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
        agency_fee = self._resolve_fee_amount(
            params.agency_fee_rate, params.property_price
        )
        notary_fee = self._resolve_fee_amount(
            params.notary_fee_rate, params.property_price
        )
        loan_rate = self._resolve_loan_rate(params)
        rent_increase = params.rent_increase_rate / 100

        total_cost = self._compute_total_cost(params, agency_fee, notary_fee)
        loan_amount = total_cost - params.down_payment

        loan = Loan(
            amount=loan_amount,
            duration_years=params.loan_duration,
            annual_rate=loan_rate,
        )
        monthly_schedule = loan.monthly_schedule()
        annual_schedule = loan.annual_schedule(params.start_month)

        death_insurance_annual = params.death_insurance_monthly * 12
        resolved_expenses = self._resolve_annual_expenses(params)
        rental = Rental(
            monthly_rent=params.monthly_rent,
            annual_expenses=resolved_expenses,
            rent_increase_rate=rent_increase,
        )
        rental_flows = rental.projected_flows(self._duration, params.start_month)

        total_acquisition_fees = agency_fee + notary_fee + params.broker_fee
        amortise_fees = params.acquisition_fees_treatment == "amortissement"

        depreciation = Depreciation(
            property_value=params.property_price,
            furniture_cost=params.furniture_cost,
            acquisition_fees=total_acquisition_fees if amortise_fees else 0.0,
        )
        depreciation_schedule = depreciation.annual_schedule(
            self._duration, params.start_month
        )

        taxation = Taxation(
            acquisition_fees_deductible=0.0 if amortise_fees else total_acquisition_fees,
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

        cashflow_df = self._build_cashflow_frame(
            rental_flows, annual_schedule, death_insurance_annual, params.start_month
        )

        resale_horizon = params.resale_horizon
        resale_value = self._compute_resale_value(params, resale_horizon)
        remaining_balance = annual_schedule[
            min(resale_horizon, len(annual_schedule)) - 1
        ].remaining_balance
        discounted_flows = self._build_discounted_flows(
            cashflow_df["Cashflow (€)"].tolist(),
            params.down_payment,
            resale_value,
            remaining_balance,
            resale_horizon,
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
            effective_loan_rate=loan_rate * 100,
            resolved_annual_expenses=resolved_expenses,
            resolved_death_insurance_annual=death_insurance_annual,
        )

    def _annualize(self, amount: float, period: str) -> float:
        """Convertit un montant périodique en montant annuel.

        Args:
            amount: Montant par période (€).
            period: Périodicité parmi "mensuel", "trimestriel", "annuel".

        Returns:
            Montant annualisé (€).
        """
        return amount * PERIOD_MULTIPLIERS.get(period, 1)

    def _resolve_annual_expenses(self, params: SimulationParams) -> float:
        """Calcule le total annuel des charges d'exploitation.

        Si au moins un champ détaillé est renseigné (> 0), la somme
        annualisée des 5 postes est utilisée. Sinon, ``annual_expenses``
        (saisie globale) est retourné directement.

        Args:
            params: Paramètres de simulation.

        Returns:
            Charges annuelles totales (€).
        """
        detailed_total = (
            self._annualize(params.pno_insurance, params.pno_period)
            + self._annualize(params.gli_insurance, params.gli_period)
            + self._annualize(
                params.agency_management_fee, params.agency_management_fee_period
            )
            + self._annualize(params.property_tax, params.property_tax_period)
            + self._annualize(params.condo_fees, params.condo_fees_period)
            + self._annualize(params.accounting_fee, params.accounting_fee_period)
        )
        if detailed_total > 0:
            return detailed_total
        return params.annual_expenses

    def _resolve_loan_rate(self, params: SimulationParams) -> float:
        """Calcule le taux effectif annuel de l'emprunt (décimal).

        Si ``loan_nominal_rate`` est renseigné (> 0), le taux effectif est la
        somme du taux nominal et du taux d'assurance TAEA. Sinon le TAEG
        ``loan_rate`` est utilisé directement.

        Args:
            params: Paramètres de simulation.

        Returns:
            Taux effectif annuel sous forme décimale.
        """
        if params.loan_nominal_rate > 0:
            return (params.loan_nominal_rate + params.loan_insurance_rate) / 100
        return params.loan_rate / 100

    def _resolve_fee_amount(self, fee_input: float, property_price: float) -> float:
        """Convertit une saisie de frais en montant absolu (€).

        Si ``fee_input`` est inférieur au seuil, il est interprété comme un
        pourcentage du prix d'achat. Sinon il est pris comme un montant fixe.

        Args:
            fee_input: Valeur saisie par l'utilisateur (% ou €).
            property_price: Prix d'achat net vendeur (€).

        Returns:
            Montant des frais en euros.
        """
        if fee_input < FEE_AMOUNT_THRESHOLD:
            return property_price * fee_input / 100
        return fee_input

    def _compute_total_cost(
        self,
        params: SimulationParams,
        agency_fee: float,
        notary_fee: float,
    ) -> float:
        """Coût total d'acquisition (prix + frais + travaux + mobilier + prêt)."""
        return (
            params.property_price
            + agency_fee
            + notary_fee
            + params.renovation_cost
            + params.furniture_cost
            + params.broker_fee
            + params.guarantee_fee
            + params.dossier_fee
        )

    def _pad_to_duration(self, values: list[float]) -> list[float]:
        """Aligne une liste sur la durée de simulation en complétant par des zéros."""
        return (values + [0.0] * self._duration)[: self._duration]

    def _build_cashflow_frame(
        self,
        rental_flows: list[YearlyRentalFlow],
        annual_schedule: list[AmortizationEntry],
        death_insurance_annual: float = 0.0,
        start_month: int = 1,
    ) -> pd.DataFrame:
        """Construit le DataFrame de cashflow annuel.

        Args:
            rental_flows: Flux locatifs annuels.
            annual_schedule: Tableau d'amortissement annuel de l'emprunt.
            death_insurance_annual: Coût annuel de l'assurance décès (€).
                Appliqué uniquement pendant la durée du prêt.
            start_month: Mois de démarrage de l'activité (1–12).
                L'assurance décès est proratisée en année 1.

        Returns:
            DataFrame avec colonnes FR prêtes pour l'affichage.
        """
        incomes = self._pad_to_duration([f.income for f in rental_flows])
        expenses = self._pad_to_duration([f.expenses for f in rental_flows])
        raw_annuities = self._pad_to_duration([e.payment for e in annual_schedule])
        first_year_death = death_insurance_annual * (13 - start_month) / 12
        death_ins_list = (
            [first_year_death] + [death_insurance_annual] * (len(annual_schedule) - 1)
            if annual_schedule
            else []
        )
        death_ins = self._pad_to_duration(death_ins_list)
        annuities = [a + d for a, d in zip(raw_annuities, death_ins)]
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

    def _compute_resale_value(
        self, params: SimulationParams, resale_horizon: int
    ) -> float:
        """Calcule la valeur de revente à l'horizon configuré.

        Interprète ``params.resale`` selon sa magnitude : en dessous du seuil
        c'est un taux d'inflation annuel appliqué au prix net vendeur, au-dessus
        c'est directement le prix de revente.

        Args:
            params: Paramètres de simulation.
            resale_horizon: Nombre d'années avant la revente.

        Returns:
            Valeur de revente (€).
        """
        if params.resale < RESALE_VALUE_THRESHOLD:
            inflation_rate = params.resale / 100
            net_price = (
                params.property_price
                + params.renovation_cost
                + params.furniture_cost
            )
            return round(net_price * (1 + inflation_rate) ** resale_horizon)
        return params.resale

    def _build_discounted_flows(
        self,
        cashflows: list[float],
        down_payment: float,
        resale_value: float,
        remaining_balance: float,
        resale_horizon: int,
    ) -> list[float]:
        """Construit la série de flux utilisée pour VAN et TRI.

        Ajoute l'apport négatif en année 1 et le solde de revente (prix de
        revente moins capital restant dû) à l'horizon.

        Args:
            cashflows: Cashflows annuels sur la durée totale de simulation.
            down_payment: Apport personnel (€).
            resale_value: Prix de revente net (€).
            remaining_balance: Capital restant dû à l'horizon (€).
            resale_horizon: Nombre d'années avant la revente.

        Returns:
            Série de flux actualisables pour VAN/TRI.
        """
        flows = list(cashflows[:resale_horizon])
        flows[0] -= down_payment
        flows[-1] += resale_value - remaining_balance
        return flows
