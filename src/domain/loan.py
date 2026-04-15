"""Entité domaine : emprunt immobilier à taux fixe."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AmortizationEntry:
    """Ligne d'un tableau d'amortissement.

    Attributes:
        period: Numéro de la période (mois ou année, 1-indexé).
        payment: Montant du remboursement sur la période (€).
        interest: Part des intérêts (€).
        principal: Part du capital remboursé (€).
        remaining_balance: Capital restant dû après la période (€).
    """

    period: int
    payment: float
    interest: float
    principal: float
    remaining_balance: float


@dataclass(frozen=True)
class Loan:
    """Emprunt immobilier à taux fixe avec mensualités constantes.

    Attributes:
        amount: Montant emprunté (€).
        duration_years: Durée de l'emprunt en années.
        annual_rate: Taux d'intérêt annuel sous forme décimale (ex: 0.035 pour 3,5 %).
    """

    amount: float
    duration_years: int
    annual_rate: float

    @property
    def duration_months(self) -> int:
        """Durée totale en mois."""
        return self.duration_years * 12

    @property
    def monthly_rate(self) -> float:
        """Taux d'intérêt mensuel."""
        return self.annual_rate / 12

    @property
    def monthly_payment(self) -> float:
        """Calcule la mensualité constante.

        Returns:
            Montant d'une mensualité (€).
        """
        if self.monthly_rate > 0:
            return (
                self.amount
                * self.monthly_rate
                / (1 - (1 + self.monthly_rate) ** -self.duration_months)
            )
        return self.amount / self.duration_months

    @property
    def total_payments(self) -> float:
        """Somme totale des remboursements sur toute la durée (€)."""
        return self.monthly_payment * self.duration_months

    @property
    def total_interest(self) -> float:
        """Coût total des intérêts sur toute la durée (€)."""
        return self.total_payments - self.amount

    def monthly_schedule(self) -> list[AmortizationEntry]:
        """Génère le tableau d'amortissement mensuel.

        Returns:
            Liste des lignes d'amortissement, une par mois.
        """
        entries: list[AmortizationEntry] = []
        remaining = self.amount
        for month in range(1, self.duration_months + 1):
            interest = remaining * self.monthly_rate
            principal = self.monthly_payment - interest
            remaining -= principal
            entries.append(
                AmortizationEntry(
                    period=month,
                    payment=self.monthly_payment,
                    interest=interest,
                    principal=principal,
                    remaining_balance=remaining,
                )
            )
        return entries

    def annual_schedule(self) -> list[AmortizationEntry]:
        """Génère le tableau d'amortissement annuel agrégé.

        Returns:
            Liste des lignes d'amortissement, une par année.
        """
        monthly = self.monthly_schedule()
        annual: list[AmortizationEntry] = []
        for year in range(1, self.duration_years + 1):
            window = monthly[(year - 1) * 12 : year * 12]
            annual.append(
                AmortizationEntry(
                    period=year,
                    payment=sum(e.payment for e in window),
                    interest=sum(e.interest for e in window),
                    principal=sum(e.principal for e in window),
                    remaining_balance=window[-1].remaining_balance,
                )
            )
        return annual
