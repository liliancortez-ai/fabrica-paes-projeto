"""Consultas relacionais parametrizadas, sem lógica de apresentação."""

from __future__ import annotations

import sqlite3
from typing import Any


def _fetch_dicts(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    """Consome o cursor e converte cada linha nomeada em um dicionário.

    A conexão deve usar ``sqlite3.Row``; o resultado é materializado em memória
    e uma consulta sem resultados retorna lista vazia.
    """
    return [dict(row) for row in cursor.fetchall()]


def list_categories(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Retorna dicionários com ID e nome das categorias, em ordem de nome.

    A conexão deve ter ``sqlite3.Row`` como fábrica de linhas. Uma tabela
    vazia produz uma lista vazia; falhas SQL são propagadas ao chamador.
    """
    return _fetch_dicts(
        connection.execute("SELECT id_categoria, nome FROM categoria ORDER BY nome")
    )


def list_ingredients(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Retorna ID, nome e unidade cadastrada de cada ingrediente.

    A ordenação é por nome e inclui ingredientes ainda não usados em receitas.
    Requer conexão configurada com linhas nomeadas.
    """
    return _fetch_dicts(
        connection.execute(
            "SELECT id_ingrediente, nome, unidade_medida FROM ingrediente ORDER BY nome"
        )
    )


def list_breads(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Retorna produtos em ordem de nome com preço, peso e categoria.

    Produtos sem categoria recebem o rótulo ``Sem categoria``; o campo
    ``id_categoria`` permanece nulo. Requer conexão com linhas nomeadas.
    """
    return _fetch_dicts(
        connection.execute(
            """SELECT p.id_pao, p.nome, p.preco, p.peso_gramas,
                      p.id_categoria, COALESCE(c.nome, 'Sem categoria') AS categoria
               FROM pao AS p
               LEFT JOIN categoria AS c ON c.id_categoria = p.id_categoria
               ORDER BY p.nome"""
        )
    )


def list_recipes(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Retorna uma linha por par pão/ingrediente, com quantidade e unidade.

    O resultado inclui IDs para filtragem e nomes para apresentação, ordenado
    por pão e ingrediente. Produtos sem receita não geram linhas. Requer
    conexão com linhas nomeadas e propaga erros SQL ao chamador.
    """
    return _fetch_dicts(
        connection.execute(
            """SELECT r.id_pao, p.nome AS pao,
                      COALESCE(c.nome, 'Sem categoria') AS categoria,
                      r.id_ingrediente, i.nome AS ingrediente,
                      r.quantidade, i.unidade_medida
               FROM pao_ingrediente AS r
               JOIN pao AS p ON p.id_pao = r.id_pao
               LEFT JOIN categoria AS c ON c.id_categoria = p.id_categoria
               JOIN ingrediente AS i ON i.id_ingrediente = r.id_ingrediente
               ORDER BY p.nome, i.nome"""
        )
    )
