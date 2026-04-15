"""Entité domaine : bien en location et projection des flux."""

from dataclasses import dataclass


@dataclass(frozen=True)
class YearlyRentalFlow:
    """Flux locatifs annuels projetés.

    Attributes:
        year: Année (1-indexée).
        income: Revenus locatifs bruts de l'année (€).
        expenses: Charges de l'année (€).
    """

    year: int
    income: float
    expenses: float


@dataclass(frozen=True)
class Rental:
    """Bien mis en location avec augmentation annuelle du loyer.

    Attributes:
        monthly_rent: Loyer mensuel de la première année (€).
        annual_expenses: Charges annuelles fixes (€).
        rent_increase_rate: Taux d'augmentation annuel du loyer (décimal).
    """

    monthly_rent: float
    annual_expenses: float
    rent_increase_rate: float

    def projected_flows(self, duration_years: int) -> list[YearlyRentalFlow]:
        """Projette les flux de revenus et de charges sur plusieurs années.

        Args:
            duration_years: Horizon de projection en années.

        Returns:
            Liste des flux annuels sur la durée demandée.
        """
        flows: list[YearlyRentalFlow] = []
        annual_rent = self.monthly_rent * 12
        for year in range(1, duration_years + 1):
            flows.append(
                YearlyRentalFlow(
                    year=year,
                    income=annual_rent,
                    expenses=self.annual_expenses,
                )
            )
            annual_rent *= 1 + self.rent_increase_rate
        return flows
