"""Migrações incrementais com controle de versão e integridade SHA-256."""

from __future__ import annotations

import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterator

from fabrica_paes.config import migration_resources


_PATTERN = re.compile(r"^\d{4}_[a-z][a-z0-9_]*\.sql$")


@dataclass(frozen=True)
class Migration:
    """Descreve uma migração imutável disponível no pacote.

    Attributes:
        version: Nome do arquivo sem a extensão SQL.
        sql: Conteúdo integral que será executado no SQLite.
        checksum: Resumo SHA-256 do conteúdo UTF-8, usado para detectar edição.
    """

    version: str
    sql: str
    checksum: str


def iter_sql_statements(source: str) -> Iterator[str]:
    """Separa comandos SQL usando o parser sintático simples do SQLite.

    Não suporta instruções com blocos de trigger; os scripts deste projeto
    contêm apenas CREATE TABLE e CREATE INDEX.

    Args:
        source: Texto integral do arquivo SQL.

    Yields:
        Cada instrução completa, incluindo comentários associados.

    Raises:
        ValueError: Se restar texto incompleto após o último delimitador.
    """
    buffer = ""
    for line in source.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            if buffer.strip() and not all(
                fragment.strip().startswith("--") or not fragment.strip()
                for fragment in buffer.splitlines()
            ):
                yield buffer
            buffer = ""
    if buffer.strip():
        raise ValueError("Migração SQL incompleta: faltou finalizar instrução com ';'.")


def available_migrations() -> list[Migration]:
    """Carrega os arquivos SQLite com nome versionado em ordem alfabética.

    Calcula o SHA-256 de cada conteúdo e ignora arquivos que não sigam o
    padrão de quatro dígitos. Lança RuntimeError se não houver migrações.
    """
    root = migration_resources()
    result = []
    for resource in sorted(root.iterdir(), key=lambda item: item.name):
        if not _PATTERN.fullmatch(resource.name):
            continue
        content = resource.read_text(encoding="utf-8")
        result.append(
            Migration(
                version=resource.name.removesuffix(".sql"),
                sql=content,
                checksum=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            )
        )
    if not result:
        raise RuntimeError("Nenhuma migração SQLite foi encontrada no pacote.")
    return result


def apply_migrations(connection: sqlite3.Connection) -> list[str]:
    """Aplica apenas migrações pendentes de forma transacional.

    Cada migração é registrada em ``schema_migrations`` com seu hash SHA-256.
    Se o conteúdo de uma migração já aplicada mudar, a função interrompe
    a execução em vez de alterar um histórico existente silenciosamente.

    Args:
        connection: Conexão SQLite aberta, com ``foreign_keys=ON``.

    Returns:
        Lista dos nomes das migrações aplicadas nesta chamada.

    Raises:
        ValueError: Em caso de alteração detectada numa migração aplicada.
        sqlite3.Error: Se algum comando SQL falhar.
    """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )"""
    )
    connection.commit()
    applied = dict(
        connection.execute("SELECT version, checksum FROM schema_migrations").fetchall()
    )
    new_versions = []
    for migration in available_migrations():
        existing_checksum = applied.get(migration.version)
        if existing_checksum is not None:
            if existing_checksum != migration.checksum:
                raise ValueError(
                    f"Migração {migration.version} foi modificada após aplicada. "
                    "Crie uma nova migração em vez de editar a anterior."
                )
            continue
        try:
            connection.execute("BEGIN IMMEDIATE")
            for statement in iter_sql_statements(migration.sql):
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations (version, checksum, applied_at) "
                "VALUES (?, ?, ?)",
                (
                    migration.version,
                    migration.checksum,
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        new_versions.append(migration.version)
    return new_versions


def migration_status(connection: sqlite3.Connection) -> list[dict[str, str | bool]]:
    """Compara migrações empacotadas com o histórico do banco.

    Retorna versão, indicação de aplicação e validade do checksum para cada
    arquivo disponível. Um banco sem tabela de histórico é tratado como vazio;
    esta consulta não aplica nem repara migrações.
    """
    try:
        installed = dict(
            connection.execute("SELECT version, checksum FROM schema_migrations").fetchall()
        )
    except sqlite3.OperationalError:
        installed = {}
    return [
        {
            "versao": migration.version,
            "aplicada": migration.version in installed,
            "checksum_valido": (
                installed.get(migration.version) == migration.checksum
                if migration.version in installed
                else False
            ),
        }
        for migration in available_migrations()
    ]
