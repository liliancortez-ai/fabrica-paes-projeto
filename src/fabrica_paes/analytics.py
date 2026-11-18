"""Cálculo independente dos indicadores consumidos pelo dashboard e pela CLI."""

from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from fabrica_paes.repository import list_breads, list_recipes


_CENT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    """Arredonda um Decimal a centavos pelo critério HALF_UP.

    Retorna outro Decimal; o arredondamento ocorre após calcular a média.
    """
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class DashboardData:
    """Indicadores calculados com os mesmos filtros do painel interativo.

    Os totais representam cadastros e composições de receitas, **não** ordens
    de produção, estoques ou vendas; essas entidades não existem no modelo.
    """

    total_paes: int
    total_ingredientes: int
    preco_medio: Decimal
    peso_medio_gramas: Decimal
    total_linhas_receitas: int
    paes: list[dict[str, Any]]
    receitas: list[dict[str, Any]]
    paes_por_categoria: list[dict[str, Any]]
    preco_medio_por_categoria: list[dict[str, Any]]
    uso_ingredientes: list[dict[str, Any]]


def build_dashboard(
    connection: sqlite3.Connection,
    *,
    categoria_id: int | None = None,
    pao_id: int | None = None,
    ingrediente_id: int | None = None,
) -> DashboardData:
    """Produz dados para o BI, aplicando filtros coerentes a todas as métricas.

    Args:
        connection: Conexão SQLite com tabelas previamente migradas.
        categoria_id: Restringe os produtos à categoria solicitada.
        pao_id: Restringe a um produto específico.
        ingrediente_id: Seleciona pães que utilizam o ingrediente informado.
            As receitas exibidas continuam completas para os pães filtrados.

    Returns:
        Indicadores e linhas para gráficos. O preço médio é a média aritmética
        dos preços dos pães selecionados, arredondada a centavos com HALF_UP;
        o peso médio é arredondado ao grama. Ingredientes distintos contam
        apenas ingredientes presentes nas receitas dos pães selecionados.
        Sem pães selecionados, médias e contagens são zero e listas vazias.

    Notes:
        Os filtros são combinados por interseção. A frequência de ingrediente
        conta pães distintos, e não quantidades físicas. Categorias sem pães
        selecionados não aparecem nas agregações. A conexão deve usar linhas
        nomeadas, como as retornadas por ``database.connect``.
    """
    breads = list_breads(connection)
    recipes = list_recipes(connection)

    if ingrediente_id is not None:
        eligible_ids = {
            recipe["id_pao"]
            for recipe in recipes
            if recipe["id_ingrediente"] == ingrediente_id
        }
        breads = [bread for bread in breads if bread["id_pao"] in eligible_ids]

    if categoria_id is not None:
        breads = [bread for bread in breads if bread["id_categoria"] == categoria_id]
    if pao_id is not None:
        breads = [bread for bread in breads if bread["id_pao"] == pao_id]

    bread_ids = {bread["id_pao"] for bread in breads}
    recipes = [recipe for recipe in recipes if recipe["id_pao"] in bread_ids]
    total = len(breads)
    average_price = (
        _money(sum((Decimal(str(bread["preco"])) for bread in breads), Decimal()) / total)
        if total
        else Decimal("0.00")
    )
    average_weight = (
        (sum((Decimal(str(bread["peso_gramas"])) for bread in breads), Decimal()) / total)
        .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        if total
        else Decimal("0")
    )

    categories: Counter[str] = Counter()
    category_prices: dict[str, list[Decimal]] = defaultdict(list)
    for bread in breads:
        name = bread["categoria"]
        categories[name] += 1
        category_prices[name].append(Decimal(str(bread["preco"])))

    ingredient_breads: dict[tuple[int, str], set[int]] = defaultdict(set)
    for recipe in recipes:
        key = (recipe["id_ingrediente"], recipe["ingrediente"])
        ingredient_breads[key].add(recipe["id_pao"])

    return DashboardData(
        total_paes=total,
        total_ingredientes=len(ingredient_breads),
        preco_medio=average_price,
        peso_medio_gramas=average_weight,
        total_linhas_receitas=len(recipes),
        paes=breads,
        receitas=recipes,
        paes_por_categoria=[
            {"categoria": name, "quantidade": count}
            for name, count in sorted(categories.items())
        ],
        preco_medio_por_categoria=[
            {
                "categoria": name,
                "preco_medio": float(
                    _money(sum(values, Decimal()) / len(values))
                ),
            }
            for name, values in sorted(category_prices.items())
        ],
        uso_ingredientes=[
            {"ingrediente": name, "total_paes": len(ids)}
            for (_id, name), ids in sorted(
                ingredient_breads.items(),
                key=lambda entry: (-len(entry[1]), entry[0][1]),
            )
        ],
    )
