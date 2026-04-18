"""Entité domaine : amortissements comptables du bien et du mobilier (LMNP)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Depreciation:
    """Plan d'amortissement linéaire du bien et du mobilier.

    Le bien est amorti sur sa durée de vie comptable, pondéré par un taux
    d'usure (la part terrain n'étant pas amortissable). Le mobilier suit
    son propre plan indépendant.

    Attributes:
        property_value: Valeur du bien hors frais (€).
        renovation_cost: Coût des travaux amortissables (€).
        furniture_cost: Coût du mobilier (€).
        property_duration: Durée d'amortissement du bien en années.
        furniture_duration: Durée d'amortissement du mobilier en années.
        property_wear_rate: Part amortissable du bien (décimal, ex: 0.8).
    """

    property_value: float
    renovation_cost: float
    furniture_cost: float
    property_duration: int = 25
    furniture_duration: int = 8
    property_wear_rate: float = 0.8

    def annual_schedule(self, duration_years: int) -> list[float]:
        """Calcule l'amortissement total annuel sur la durée demandée.

        Args:
            duration_years: Horizon de projection en années.

        Returns:
            Liste des montants d'amortissement annuel (€).
        """
        property_amount = (
            (self.property_value + self.renovation_cost)
            * self.property_wear_rate
            / self.property_duration
        )
        furniture_amount = self.furniture_cost / self.furniture_duration

        schedule: list[float] = []
        for year in range(1, duration_years + 1):
            total = 0.0
            if year <= self.property_duration:
                total += property_amount
            if year <= self.furniture_duration:
                total += furniture_amount
            schedule.append(total)
        return schedule
