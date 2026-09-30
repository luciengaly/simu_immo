### Roadmap
- [x] Possibilité d'entrer un mois de l'année comme début de l'activité
- [x] Entrer les frais d'agence en % ou en € selon l'ordre de grandeur
- [x] Entrer les frais d'acte (notaire + enregistrmement) en % ou en € selon l'ordre de grandeur
- [x] Possibilité d'entrer un TAEG, ou un Taux nominal de prêt et un TAEA séparément
- [x] Détailler les champs charges : Assurance PNO, Assurance GLI, Honoraires agence location, Taxe foncière, Charges de copro
- [x] Prix fixe de revente (net vendeur) + nombre d'année à entrer dans ce cas là
- [x] Possibilité de modifier les unités temporelles des champs, par exemple : entrer les loyers par mois, ou par an - entrer la taxe foncière par mois, trimestre, ou par an - idem pour les charges de copro
- [ ] Possibilité de modifier en cours de simulation de dire qu'un champs va changer, par exemple : si un locataire est déjà en place et paie un montant de loyer, et qu'il y a une honoraire d'agence de location, ajouter le fait de simuler qu'à partir d'un certain mois d'une année, cela change, pour par exemple s'exempter d'agence de location, et augmenter son loyer. 
- [x] Ajout optionnel Frais de garantie pour le prêt
- [x] Ajout optionnel Frais de dossier pour le prêt
- [x] Ajout optionnel Frais de comptabilité pour l'exploitation
- [x] Ajout de frais d'exploitation fixes nommés avec proposition : assurance Décès (x € par mois souscrit au moment du prêt)
- [x] Mention "Sans travaux" dans le bandeau récapitulatif si montant travaux et ammeublement à 0 €
- [x] Affinement du calcul de l'amortissement selon les modalités suivantes : 
Amortissements		
Composants	Part	Amortissable
Terrain	20%	Non
Gros oeuvre	50%	50 ans
Façades et étanchéités	5%	20 ans
Installations générales, électricité	5%	25 ans
Agencements	20%	15 ans
- [x] Tableau fiscal selon 2 choix : déduction des frais d'acquisition ou amortissement des frais d'acquisition (agence + notaire-acte + courtier). 
- [x] Fournir une nouvelle vue récapitulative avec les champs suivants :
Coût total de l'investissement
APPORT
MONTANT DU PRÊT
Taux d'intérêt
Taux d'assurance
Durée du prêt
Charges mensuelles
MENSUALITÉS DE PRÊT
Loyer
Rendement net de frais d'acquisition
Rendement net de charges d'exploitation
TRÉSORERIE MENSUELLE
Gain net a 10 ans*
Taux de Rendement Interne simplifié à 10 ans*
- [ ] Export Excel d'un rapport d'investissement
- [x] Page à propos avec Auteur et petites infos diverses
- [x] Refonte de l'accueil pour présenter le simulateur. 
- [x] Refonte du calcul du résultat comptable et fiscal : 
Le Calcul Rigoureux du Résultat Fiscal
Étape 1 — Recettes brutes
Total des loyers encaissés
Étape 2 — Déduction des charges courantes
Toutes les charges d'exploitation déductibles : taxe foncière, CFE, intérêts d'emprunt, assurances, frais de gestion, frais de comptabilité, charges de copropriété non récupérables, etc.
Ce résultat intermédiaire s'appelle le résultat avant amortissement (ou "bénéfice courant"). Il peut être négatif → dans ce cas, il constitue un déficit de charges, reportable sur 10 ans sur les revenus BIC meublés.
Étape 3 — Déduction des amortissements (plafonnée)
'amortissement est déduit à hauteur du résultat intermédiaire positif de l'étape 2.
Le plafond est : Amortissement déductible ≤ Loyers − Charges courantes déductibles
L'excédent d'amortissement non déduit devient un amortissement reportable, sans limite de durée
Étape 4 — Imputation des déficits et amortissements reportés des années antérieures
Ce n'est qu'en dernier ressort que l'on puie dans les stocks de reports antérieurs, si le résultat après étape 3 est encore positif
Tableau des Priorités de Déduction
Rang	Élément	Règle	Conséquence si excédent
1	Charges courantes (intérêts, taxe foncière, frais de gestion…)	Déductibles sans plafond	Crée un déficit reportable 10 ans (BIC meublé uniquement)
2	Amortissements de l'année (bâti, mobilier…)	Plafonnés : ne peuvent pas créer de déficit	Excédent = amortissement reportable sans limite de durée
3	Amortissements reportés des années antérieures	Imputables sur résultat positif après étapes 1+2	Excédent reporte encore à nouveau
4	Déficits de charges reportés (≤ 10 ans)	Imputables sur résultat positif BIC meublé	Purge dans l'ordre chronologique (FIFO)
- [ ] Si taux inflation pour calcul revente, créer une vue de l'évolution du TRI et de l'évolution de l'enrichissement pour les différentes valeurs de revente chaque année
- [x] Le TAEG doit intgrer les frais de dossier et de garantie donc ceux là ne doivent pas apparaitre dans cette vue, alors que le taux nominal et taux d'assurance peuvent être complétée par ce genre de frais