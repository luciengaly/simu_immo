"""Entité domaine : amortissements comptables du bien et du mobilier (LMNP)."""

from dataclasses import dataclass


# Composants réglementaires du bien immobilier :
# (libellé, part du prix net vendeur, durée en années — 0 = non amortissable)
PROPERTY_COMPONENTS: list[tuple[str, float, int]] = [
    ("Terrain", 0.20, 0),
    ("Gros œuvre", 0.50, 50),
    ("Façades et étanchéités", 0.05, 20),
    ("Installations générales", 0.05, 25),
    ("Agencements", 0.20, 15),
]

FURNITURE_DURATION: int = 5


@dataclass(frozen=True)
class DepreciationComponent:
    """Composant d'amortissement d'un bien immobilier.

    Attributes:
        name: Libellé du composant.
        base_amount: Valeur de base du composant (€).
        annual_amount: Dotation annuelle d'amortissement (€).
        duration_years: Durée d'amortissement (années). 0 = non amortissable.
    """

    name: str
    base_amount: float
    annual_amount: float
    duration_years: int


@dataclass(frozen=True)
class Depreciation:
    """Plan d'amortissement par composants du bien et du mobilier (LMNP).

    Le bien (prix net vendeur) est décomposé en 5 composants réglementaires.
    Le terrain (20 %) n'est pas amortissable. Les travaux de rénovation sont
    traités comme charges déductibles et n'entrent pas dans la base amortissable.
    Le mobilier est amorti séparément sur sa propre durée.

    En mode amortissement des frais d'acquisition, ceux-ci s'ajoutent à
    ``property_value`` pour constituer la base fiscale amortissable totale.
    Les composants existants s'appliquent alors sur cette valeur augmentée.

    Attributes:
        property_value: Prix d'achat net vendeur (€).
        furniture_cost: Coût du mobilier (€).
        acquisition_fees: Frais d'acquisition à amortir (agence + notaire +
            courtier, €). 0 en mode déduction.
    """

    property_value: float
    furniture_cost: float
    acquisition_fees: float = 0.0

    def components(self) -> list[DepreciationComponent]:
        """Retourne le détail des composants d'amortissement du bien et du mobilier.

        Returns:
            Liste des composants avec leur dotation annuelle respective.
        """
        fiscal_base = self.property_value + self.acquisition_fees
        result: list[DepreciationComponent] = []
        for name, share, duration in PROPERTY_COMPONENTS:
            base = fiscal_base * share
            annual = base / duration if duration > 0 else 0.0
            result.append(
                DepreciationComponent(
                    name=name,
                    base_amount=round(base, 2),
                    annual_amount=round(annual, 2),
                    duration_years=duration,
                )
            )
        furniture_annual = (
            self.furniture_cost / FURNITURE_DURATION if self.furniture_cost > 0 else 0.0
        )
        result.append(
            DepreciationComponent(
                name="Mobilier",
                base_amount=self.furniture_cost,
                annual_amount=round(furniture_annual, 2),
                duration_years=FURNITURE_DURATION,
            )
        )
        return result

    def annual_schedule(
        self, duration_years: int, start_month: int = 1
    ) -> list[float]:
        """Calcule l'amortissement total annuel sur la durée demandée.

        Si ``start_month`` est supérieur à 1, l'année 1 est proratisée au
        nombre de mois détenus (``13 - start_month``). L'année suivant la fin
        de chaque composant reçoit les mois restants
        (``start_month - 1``), garantissant que la somme amortie sur toute la
        durée du composant est exacte.

        Args:
            duration_years: Horizon de projection en années.
            start_month: Mois de démarrage de l'activité (1 = janvier,
                12 = décembre).

        Returns:
            Liste des montants d'amortissement annuel (€).
        """
        proration = (13 - start_month) / 12
        tail = (start_month - 1) / 12
        comps = self.components()
        schedule: list[float] = []
        for year in range(1, duration_years + 1):
            total = 0.0
            for c in comps:
                if c.duration_years == 0:
                    continue
                if year == 1:
                    total += c.annual_amount * proration
                elif year <= c.duration_years:
                    total += c.annual_amount
                elif year == c.duration_years + 1 and start_month > 1:
                    total += c.annual_amount * tail
            schedule.append(round(total, 2))
        return schedule
