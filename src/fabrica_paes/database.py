"""Abertura e configuração de conexões para SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fabrica_paes.config import database_path


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    """Abre um banco SQLite com chaves estrangeiras habilitadas.

    Args:
        path: Caminho do arquivo do banco. Usa ``FABRICA_PAES_DB`` ou
            ``./fabrica_paes.sqlite3`` quando omitido. Aceita ``:memory:``.

    Returns:
        Conexão cuja leitura de linhas permite acesso por nome de coluna.
        O chamador deve fechá-la e controlar as transações. A conexão ativa
        chaves estrangeiras e aguarda até cinco segundos por bloqueios.

    Raises:
        sqlite3.Error: Se não for possível abrir ou configurar o banco.
    """
    destination = str(path if path is not None else database_path())
    if destination != ":memory:":
        Path(destination).expanduser().parent.mkdir(parents=True, exist_ok=True)
        destination = str(Path(destination).expanduser())
    connection = sqlite3.connect(destination)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
    except Exception:
        connection.close()
        raise
    return connection
