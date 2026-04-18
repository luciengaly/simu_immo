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

    def projected_flows(
        self, duration_years: int, start_month: int = 1
    ) -> list[YearlyRentalFlow]:
        """Projette les flux de revenus et de charges sur plusieurs années.

        Si ``start_month`` est supérieur à 1, les revenus et charges de la
        première année sont proratisés au nombre de mois restants
        (``13 - start_month``). Les années suivantes sont complètes.

        Args:
            duration_years: Horizon de projection en années.
            start_month: Mois de démarrage de l'activité (1 = janvier,
                12 = décembre).

        Returns:
            Liste des flux annuels sur la durée demandée.
        """
        flows: list[YearlyRentalFlow] = []
        annual_rent = self.monthly_rent * 12
        for year in range(1, duration_years + 1):
            proration = (13 - start_month) / 12 if year == 1 else 1.0
            flows.append(
                YearlyRentalFlow(
                    year=year,
                    income=round(annual_rent * proration, 2),
                    expenses=round(self.annual_expenses * proration, 2),
                )
            )
            annual_rent *= 1 + self.rent_increase_rate
        return flows
