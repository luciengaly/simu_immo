"""DTO des paramètres d'entrée d'une simulation LMNP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationParams:
    """Paramètres utilisateur d'une simulation.

    Les taux (frais, emprunt, augmentation loyer) sont exprimés en
    pourcentage (ex: 3.5 pour 3,5 %) et non en décimal : la conversion
    a lieu dans la couche application.

    Pour ``agency_fee_rate`` et ``notary_fee_rate``, la saisie est libre :
    si la valeur est < 100 elle est interprétée comme un pourcentage du prix
    d'achat, sinon comme un montant fixe en euros.

    Attributes:
        property_type: Type de bien ("Appartement" ou "Maison").
        city: Ville du bien.
        surface: Surface habitable (m²).
        dpe: Note DPE (A à G).
        property_price: Prix d'achat net vendeur (€).
        agency_fee_rate: Frais d'agence (% si < 100, sinon €).
        notary_fee_rate: Frais de notaire/acte (% si < 100, sinon €).
        renovation_cost: Montant des travaux (€).
        furniture_cost: Montant du mobilier (€).
        down_payment: Apport personnel (€).
        loan_rate: TAEG tous frais inclus (%). Ignoré si loan_nominal_rate > 0.
        loan_nominal_rate: Taux nominal du prêt (%). Si > 0, prioritaire sur loan_rate.
        loan_insurance_rate: Taux d'assurance emprunteur TAEA (%). Utilisé avec loan_nominal_rate.
        loan_duration: Durée de l'emprunt (années).
        monthly_rent: Loyer mensuel (€).
        annual_expenses: Charges annuelles (€).
        rent_increase_rate: Augmentation annuelle du loyer (%).
        resale: Prix de revente (€) si > 100, sinon taux d'inflation annuel (%).
        guarantee_fee: Frais de garantie du prêt (€, 0 si absent).
        dossier_fee: Frais de dossier bancaire (€, 0 si absent).
        pno_insurance: Assurance PNO (€, 0 si mode global).
        pno_period: Périodicité de l'assurance PNO ("mensuel", "trimestriel", "annuel").
        gli_insurance: Assurance GLI (€, 0 si mode global).
        gli_period: Périodicité de l'assurance GLI.
        agency_management_fee: Honoraires agence de gestion locative (€, 0 si mode global).
        agency_management_fee_period: Périodicité des honoraires de gestion.
        property_tax: Taxe foncière (€, 0 si mode global).
        property_tax_period: Périodicité de la taxe foncière.
        condo_fees: Charges de copropriété (€, 0 si mode global).
        condo_fees_period: Périodicité des charges de copropriété.
        accounting_fee: Frais de comptabilité (€, 0 si absent).
        accounting_fee_period: Périodicité des frais de comptabilité.
        death_insurance_monthly: Assurance décès mensuelle liée au prêt (€, 0 si absent).
    """

    # Champs obligatoires
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
    # Champs optionnels (valeur 0 = absent / mode global actif)
    loan_nominal_rate: float = 0.0
    loan_insurance_rate: float = 0.0
    guarantee_fee: float = 0.0
    dossier_fee: float = 0.0
    pno_insurance: float = 0.0
    pno_period: str = "mensuel"
    gli_insurance: float = 0.0
    gli_period: str = "mensuel"
    agency_management_fee: float = 0.0
    agency_management_fee_period: str = "mensuel"
    property_tax: float = 0.0
    property_tax_period: str = "annuel"
    condo_fees: float = 0.0
    condo_fees_period: str = "trimestriel"
    accounting_fee: float = 0.0
    accounting_fee_period: str = "annuel"
    death_insurance_monthly: float = 0.0
    resale_horizon: int = 10
    start_month: int = 1
