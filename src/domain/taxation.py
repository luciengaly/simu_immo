"""Entité domaine : calcul fiscal LMNP en régime réel."""

from dataclasses import dataclass


DEFICIT_CARRY_LIMIT: int = 10  # Durée maximale de report des déficits de charges (ans)


@dataclass(frozen=True)
class TaxationEntry:
    """Ligne annuelle du tableau fiscal en 4 étapes réglementaires.

    Attributes:
        year: Année (1-indexée).
        income: Revenus locatifs bruts (€).
        current_expenses: Charges courantes déductibles — exploitation,
            intérêts d'emprunt et frais d'acquisition en année 1 (€).
        result_before_amort: Résultat avant amortissement = income − current_expenses.
            Peut être négatif (déficit de charges). (€)
        depreciation: Dotation aux amortissements de l'année (€).
        depreciation_used: Amortissement de l'année effectivement déduit
            (plafonné au résultat avant amort. positif). (€)
        carry_depreciation_used: Amortissements reportés d'années antérieures
            imputés sur le résultat de cette année (étape 3). (€)
        carry_forward_depreciation: Stock d'amortissements reportables en fin
            d'année (sans limite de durée). (€)
        deficit_added: Déficit de charges ajouté au stock cette année
            (= max(0, −result_before_amort)). (€)
        deficit_used: Déficits de charges reportés imputés sur le résultat
            de cette année (étape 4, FIFO). (€)
        carry_forward_deficit: Stock de déficits de charges reportables en
            fin d'année (max 10 ans). (€)
        fiscal_result: Résultat fiscal final après toutes imputations (≥ 0). (€)
        taxable_real: Montant imposable en régime réel (= fiscal_result). (€)
        taxable_bic: Montant imposable en régime micro-BIC (loyers × 50 %). (€)
    """

    year: int
    income: float
    current_expenses: float
    result_before_amort: float
    depreciation: float
    depreciation_used: float
    carry_depreciation_used: float
    carry_forward_depreciation: float
    deficit_added: float
    deficit_used: float
    carry_forward_deficit: float
    fiscal_result: float
    taxable_real: float
    taxable_bic: float


@dataclass(frozen=True)
class Taxation:
    """Calcul fiscal en régime réel avec déficit et amortissement reportables.

    Attributes:
        acquisition_fees_deductible: Montant total des frais d'acquisition
            déductibles en année 1 (agence + notaire + courtier, €).
            Passer 0.0 en mode amortissement.
        bic_rate: Abattement micro-BIC (décimal, défaut 0,5 soit 50 %).
    """

    acquisition_fees_deductible: float
    bic_rate: float = 0.50

    def compute(
        self,
        incomes: list[float],
        expenses: list[float],
        loan_interests: list[float],
        depreciations: list[float],
    ) -> list[TaxationEntry]:
        """Calcule le tableau fiscal annuel selon les 4 étapes réglementaires.

        Ordre d'imputation strict :
        1. Charges courantes (sans plafond) — crée un déficit reportable
           sur 10 ans si le résultat est négatif.
        2. Amortissements de l'année (plafonnés au résultat positif) —
           l'excédent non déduit est reportable sans limite de durée.
        3. Amortissements reportés des années antérieures — imputés sur
           le résultat encore positif après étape 2.
        4. Déficits de charges reportés (FIFO, ≤ 10 ans) — imputés en
           dernier ressort.

        Args:
            incomes: Revenus locatifs annuels (€).
            expenses: Charges annuelles hors intérêts d'emprunt (€).
            loan_interests: Intérêts d'emprunt annuels (€).
            depreciations: Amortissements annuels (€).

        Returns:
            Liste des lignes fiscales annuelles.
        """
        entries: list[TaxationEntry] = []
        # Stock déficits : liste de (année_origine, montant) pour gestion FIFO
        deficit_stock: list[tuple[int, float]] = []
        carry_depreciation = 0.0
        acquisition_fees = self.acquisition_fees_deductible

        for i, income in enumerate(incomes):
            year = i + 1

            # Purge des déficits expirés (> 10 ans)
            deficit_stock = [
                (y, a) for y, a in deficit_stock
                if year - y <= DEFICIT_CARRY_LIMIT
            ]

            # --- Étape 1 : charges courantes ---
            current_exp = expenses[i] + loan_interests[i]
            if year == 1:
                current_exp += acquisition_fees
            depreciation = depreciations[i]
            result_before_amort = income - current_exp

            if result_before_amort < 0:
                # Déficit de charges : reporter amortissements et déficit
                deficit_added = abs(result_before_amort)
                deficit_stock.append((year, deficit_added))
                carry_depreciation += depreciation
                depreciation_used = 0.0
                carry_depreciation_used = 0.0
                deficit_used = 0.0
                fiscal_result = 0.0
            else:
                deficit_added = 0.0
                remaining = result_before_amort

                # --- Étape 2 : amortissements de l'année (plafonnés) ---
                depreciation_used = min(remaining, depreciation)
                remaining -= depreciation_used
                carry_depreciation += depreciation - depreciation_used

                # --- Étape 3 : amortissements reportés ---
                carry_depreciation_used = min(remaining, carry_depreciation)
                remaining -= carry_depreciation_used
                carry_depreciation -= carry_depreciation_used

                # --- Étape 4 : déficits reportés (FIFO) ---
                deficit_used = 0.0
                new_deficit_stock: list[tuple[int, float]] = []
                for deficit_year, amt in deficit_stock:
                    if remaining <= 0:
                        new_deficit_stock.append((deficit_year, amt))
                        continue
                    used = min(remaining, amt)
                    deficit_used += used
                    remaining -= used
                    if amt - used > 0:
                        new_deficit_stock.append((deficit_year, amt - used))
                deficit_stock = new_deficit_stock

                fiscal_result = max(0.0, remaining)

            carry_forward_deficit = sum(a for _, a in deficit_stock)

            entries.append(
                TaxationEntry(
                    year=year,
                    income=round(income, 2),
                    current_expenses=round(current_exp, 2),
                    result_before_amort=round(result_before_amort, 2),
                    depreciation=round(depreciation, 2),
                    depreciation_used=round(depreciation_used, 2),
                    carry_depreciation_used=round(carry_depreciation_used, 2),
                    carry_forward_depreciation=round(carry_depreciation, 2),
                    deficit_added=round(deficit_added, 2),
                    deficit_used=round(deficit_used, 2),
                    carry_forward_deficit=round(carry_forward_deficit, 2),
                    fiscal_result=round(fiscal_result, 2),
                    taxable_real=round(fiscal_result, 2),
                    taxable_bic=round(income * self.bic_rate, 2),
                )
            )

        return entries
