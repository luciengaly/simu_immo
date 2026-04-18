"""Chargement de la configuration par défaut depuis un fichier YAML."""

from pathlib import Path

import yaml

from application.params import SimulationParams


def load_default_params(path: Path | str) -> SimulationParams:
    """Charge les paramètres de simulation depuis un fichier YAML.

    Les clés du YAML doivent correspondre exactement aux attributs de
    ``SimulationParams``.

    Args:
        path: Chemin vers le fichier YAML.

    Returns:
        Paramètres de simulation typés.
    """
    with open(path, "r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)
    return SimulationParams(**raw)
