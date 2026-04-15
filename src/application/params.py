"""DTO des paramètres d'entrée d'une simulation LMNP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationParams:
    """Paramètres utilisateur d'une simulation.

    Les taux (frais, emprunt, augmentation loyer) sont exprimés en
    pourcentage (ex: 3.5 pour 3,5 %) et non en décimal : la conversion
    a lieu dans la couche application.

    Attributes:
        property_type: Type de bien ("Appartement" ou "Maison").
        city: Ville du bien.
        surface: Surface habitable (m²).
        dpe: Note DPE (A à G).
        property_price: Prix d'achat net vendeur (€).
        agency_fee_rate: Frais d'agence (%).
        notary_fee_rate: Frais de notaire (%).
        renovation_cost: Montant des travaux (€).
        furniture_cost: Montant du mobilier (€).
        down_payment: Apport personnel (€).
        loan_rate: Taux d'emprunt tous frais inclus (%).
        loan_duration: Durée de l'emprunt (années).
        monthly_rent: Loyer mensuel (€).
        annual_expenses: Charges annuelles (€).
        rent_increase_rate: Augmentation annuelle du loyer (%).
        resale: Prix de revente (€) si > 100, sinon taux d'inflation annuel (%).
    """

    property_type: str
    city: str
    surface: float
    dpe: str
    property_price: float
    agency_fee_rate: float
    notary_fee_rate: float
    renovation_cost: float
    furniture_cost: float
    down_payment: float
    loan_rate: float
    loan_duration: int
    monthly_rent: float
    annual_expenses: float
    rent_increase_rate: float
    resale: float
