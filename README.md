# Simulateur LMNP

Application Streamlit de simulation d'un investissement immobilier en
Location Meublée Non Professionnelle (LMNP) au régime réel. Calcule
l'emprunt, les flux locatifs, la fiscalité (avec déficit et amortissement
reportables) et les indicateurs de revente (VAN, TRI).

## Lancement

```bash
pip install -r requirements.txt
cd src
streamlit run app.py
```

## Architecture

Le projet suit les principes de **Clean Architecture** avec des dépendances
unidirectionnelles : `presentation → application → domain`, et
`infrastructure → domain`.

```
src/
├── app.py                      # Point d'entrée Streamlit
├── domain/                     # Entités métier pures (sans dépendance externe)
│   ├── loan.py                 # Emprunt et tableau d'amortissement
│   ├── rental.py               # Location et projection des flux
│   ├── depreciation.py         # Plan d'amortissement comptable
│   └── taxation.py             # Calcul fiscal régime réel
├── application/                # Cas d'usage et orchestration
│   ├── params.py               # DTO des paramètres utilisateur
│   └── simulation.py           # Cas d'usage principal LMNPSimulation
├── infrastructure/             # Accès aux systèmes externes
│   └── config.py               # Chargement YAML
├── presentation/               # Composants d'interface
│   ├── charts.py               # Figures Plotly
│   └── components.py           # Widgets Streamlit partagés
└── pages/                      # Pages Streamlit
    ├── home.py                 # Formulaire de saisie
    ├── summary.py              # Indicateurs clés
    ├── profitability.py        # Rendements et cashflow
    ├── loan.py                 # Détail de l'emprunt
    ├── taxes.py                # Tableau fiscal
    └── resale.py               # VAN, TRI, optimisation fiscale
```

## Conventions

- **PEP 8** et **type hints** systématiques.
- **Docstrings Google-style** en français.
- Noms de symboles (classes, fonctions, variables) en anglais.
- Libellés UI et colonnes de tableaux d'affichage en français.
- Entités du domaine immuables (`@dataclass(frozen=True)`) — pas de
  dépendance à Streamlit, Pandas ou Plotly dans `domain/`.

## Configuration

Les paramètres par défaut sont dans [default.yaml](default.yaml). Les clés
correspondent exactement aux attributs de
[`SimulationParams`](src/application/params.py).
