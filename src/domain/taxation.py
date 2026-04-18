"""Entité domaine : calcul fiscal LMNP en régime réel."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TaxationEntry:
    """Ligne annuelle du tableau fiscal.

    Attributes:
        year: Année (1-indexée).
        income: Revenus locatifs de l'année (€).
        deductible_expenses: Charges déductibles, intérêts d'emprunt inclus (€).
        result: Résultat comptable avant amortissement (€).
        fiscal_result: Résultat fiscal après imputation déficit et amortissement (€).
        carry_forward_deficit: Déficit reportable cumulé en fin d'année (€).
        depreciation: Amortissement comptable de l'année (€).
        carry_forward_depreciation: Amortissement reportable cumulé en fin d'année (€).
        taxable_real: Montant imposable en régime réel (€).
        taxable_bic: Montant imposable en régime micro-BIC (€).
    """

    year: int
    income: float
    deductible_expenses: float
    result: float
    fiscal_result: float
    carry_forward_deficit: float
    depreciation: float
    carry_forward_depreciation: float
    taxable_real: float
    taxable_bic: float


@dataclass(frozen=True)
class Taxation:
    """Calcul fiscal en régime réel avec déficit et amortissement reportables.

    Attributes:
        property_value: Prix d'achat du bien (€).
        agency_fee_rate: Taux de frais d'agence (décimal).
        notary_fee_rate: Taux de frais de notaire (décimal).
        bic_rate: Part imposable en micro-BIC (décimal, défaut 0,5 soit abattement 50 %).
    """

    property_value: float
    agency_fee_rate: float
    notary_fee_rate: float
    bic_rate: float = 0.50

    def compute(
        self,
        incomes: list[float],
        expenses: list[float],
        loan_interests: list[float],
        depreciations: list[float],
    ) -> list[TaxationEntry]:
        """Calcule le tableau fiscal annuel.

        Les frais d'agence et de notaire sont imputés comme charges déductibles
        en première année. Le déficit éventuel est reporté, et les amortissements
        ne peuvent être imputés que dans la limite d'un résultat bénéficiaire.

        Args:
            incomes: Revenus locatifs annuels (€).
            expenses: Charges annuelles hors intérêts d'emprunt (€).
            loan_interests: Intérêts d'emprunt annuels (€).
            depreciations: Amortissements annuels (€).

        Returns:
            Liste des lignes fiscales annuelles, une par année d'entrée.
        """
        entries: list[TaxationEntry] = []
        carry_deficit = 0.0
        carry_depreciation = 0.0

        for i, income in enumerate(incomes):
            year = i + 1
            expense = expenses[i] + loan_interests[i]
            depreciation = depreciations[i]

            if year == 1:
                expense += self.property_value * (
                    self.agency_fee_rate + self.notary_fee_rate
                )

            result = income - expense

            if result < 0:
                fiscal_result = result + carry_deficit
                carry_deficit += abs(result)
                taxable_real = 0.0
                carry_depreciation += depreciation
            else:
                fiscal_result = result
                if carry_deficit > 0:
                    offset = min(fiscal_result, carry_deficit)
                    fiscal_result -= offset
                    carry_deficit -= offset

                if fiscal_result > 0:
                    used = min(fiscal_result, depreciation + carry_depreciation)
                    fiscal_result -= used
                    carry_depreciation += depreciation - used
                else:
                    carry_depreciation += depreciation

                taxable_real = max(0.0, fiscal_result)

            taxable_bic = income * self.bic_rate

            entries.append(
                TaxationEntry(
                    year=year,
                    income=income,
                    deductible_expenses=expense,
                    result=result,
                    fiscal_result=fiscal_result,
                    carry_forward_deficit=carry_deficit,
                    depreciation=depreciation,
                    carry_forward_depreciation=carry_depreciation,
                    taxable_real=taxable_real,
                    taxable_bic=taxable_bic,
                )
            )

        return entries
