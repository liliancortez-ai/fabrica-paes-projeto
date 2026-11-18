"""Configurações de caminhos locais e acesso aos recursos empacotados."""

from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path
from typing import Any


PACKAGE = "fabrica_paes"


def database_path() -> Path:
    """Retorna o caminho do SQLite, respeitando ``FABRICA_PAES_DB``.

    O arquivo padrão é criado no diretório de execução, não no código-fonte.
    """
    return Path(os.environ.get("FABRICA_PAES_DB", "fabrica_paes.sqlite3")).expanduser()


def migration_resources() -> Any:
    """Localiza os scripts SQLite distribuídos com o pacote.

    Returns:
        Recurso navegável de ``importlib.resources``; pode estar dentro de
        uma distribuição empacotada e não ser um diretório físico comum.
    """
    return files(PACKAGE).joinpath("resources", "migrations", "sqlite")


def seed_resources() -> Any:
    """Localiza os CSVs demonstrativos incluídos na distribuição.

    Returns:
        Recurso navegável contendo os arquivos usados por ``seed_demo``.
        Seu conteúdo é simulado e não constitui dados reais da fábrica.
    """
    return files(PACKAGE).joinpath("resources", "seed")
