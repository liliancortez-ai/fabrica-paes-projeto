"""Carga demonstrativa idempotente a partir de arquivos CSV versionados."""

from __future__ import annotations

import csv
import sqlite3
from decimal import Decimal, InvalidOperation
from typing import Any

from fabrica_paes.config import seed_resources


_DATASETS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("categorias.csv", ("id_categoria", "nome"), "categoria"),
    (
        "ingredientes.csv",
        ("id_ingrediente", "nome", "unidade_medida"),
        "ingrediente",
    ),
    (
        "paes.csv",
        ("id_pao", "nome", "preco", "peso_gramas", "id_categoria"),
        "pao",
    ),
    (
        "receitas.csv",
        ("id_pao", "id_ingrediente", "quantidade"),
        "pao_ingrediente",
    ),
)


def _read_csv(name: str, expected_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    """Lê um CSV empacotado e verifica cabeçalho e campos obrigatórios.

    Args:
        name: Nome do recurso dentro do diretório de dados demonstrativos.
        expected_fields: Colunas esperadas, na ordem exata do cabeçalho.

    Returns:
        Registros como dicionários de strings. UTF-8 com BOM é aceito.

    Raises:
        ValueError: Se o cabeçalho divergir ou houver campo vazio.
    """
    resource = seed_resources().joinpath(name)
    with resource.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected_fields:
            raise ValueError(f"Cabeçalho inválido no arquivo {name}.")
        result = []
        for number, row in enumerate(reader, start=2):
            if any(value is None or not value.strip() for value in row.values()):
                raise ValueError(f"Valor ausente em {name}, linha {number}.")
            result.append(row)
    return result


def _normalize_row(table: str, row: dict[str, str]) -> tuple[Any, ...]:
    """Converte um registro CSV para os valores aceitos pela tabela de destino.

    IDs e pesos são inteiros; preço e quantidade são convertidos por Decimal
    e fornecidos ao SQLite como strings. Nomes e unidades têm espaços nas
    extremidades removidos. Valores inválidos ou tabela desconhecida geram
    ValueError; restrições adicionais são verificadas pelo banco.
    """
    try:
        if table == "categoria":
            return int(row["id_categoria"]), row["nome"].strip()
        if table == "ingrediente":
            return (
                int(row["id_ingrediente"]),
                row["nome"].strip(),
                row["unidade_medida"].strip(),
            )
        if table == "pao":
            return (
                int(row["id_pao"]),
                row["nome"].strip(),
                str(Decimal(row["preco"])),
                int(row["peso_gramas"]),
                int(row["id_categoria"]),
            )
        if table == "pao_ingrediente":
            return (
                int(row["id_pao"]),
                int(row["id_ingrediente"]),
                str(Decimal(row["quantidade"])),
            )
    except (ValueError, InvalidOperation, KeyError) as error:
        raise ValueError(f"Registro inválido em {table}: {row}") from error
    raise ValueError(f"Tabela não reconhecida: {table}")


def seed_demo(connection: sqlite3.Connection) -> dict[str, int]:
    """Insere ou atualiza os dados demonstrativos, sem apagar dados próprios.

    Deve ser executado depois de ``apply_migrations``. Usa UPSERT, portanto
    repetir a carga não duplica as categorias, os produtos ou as receitas.
    IDs existentes nos arquivos são atualizados, inclusive seus atributos;
    registros ausentes dos CSVs não são removidos. Toda a carga é executada
    em uma transação: uma falha reverte as alterações dessa chamada.

    Args:
        connection: Conexão ao SQLite já migrado.

    Returns:
        Dicionário com a quantidade de linhas lidas de cada CSV.

    Raises:
        sqlite3.Error: Se houver violação das restrições relacionais.
        ValueError: Se um arquivo CSV estiver inválido.
    """
    counts = {}
    # Os nomes de colunas vêm exclusivamente de metadados constantes locais.
    with connection:
        for filename, fields, table in _DATASETS:
            rows = [_normalize_row(table, r) for r in _read_csv(filename, fields)]
            columns = ", ".join(fields)
            placeholders = ", ".join("?" for _ in fields)
            primary_fields = (
                ("id_pao", "id_ingrediente")
                if table == "pao_ingrediente"
                else (fields[0],)
            )
            update_fields = [field for field in fields if field not in primary_fields]
            assignments = ", ".join(f"{field} = excluded.{field}" for field in update_fields)
            statement = (
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
                f"ON CONFLICT ({', '.join(primary_fields)}) DO UPDATE SET {assignments}"
            )
            connection.executemany(statement, rows)
            counts[table] = len(rows)
    return counts
