"""Exportação de relatórios tabulares em CSV (compatível com Excel)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from fabrica_paes.analytics import DashboardData


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    """Grava linhas em UTF-8 com BOM e separador ponto e vírgula.

    O cabeçalho segue ``fields``; campos adicionais são ignorados. O arquivo
    existente é sobrescrito e erros de escrita são propagados ao chamador.
    """
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def export_reports(data: DashboardData, output_directory: str | Path) -> list[Path]:
    """Exporta os dados filtrados do painel para arquivos CSV separados.

    Args:
        data: Indicadores previamente calculados por ``build_dashboard``.
        output_directory: Diretório de destino, criado se não existir.

    Returns:
        Lista dos cinco caminhos gerados: pães, receitas, distribuição por
        categoria, preço médio por categoria e frequência de ingredientes.

    Notes:
        Arquivos de mesmo nome são sobrescritos. Os dados refletem exatamente
        os filtros aplicados anteriormente a ``data``; o diretório é criado
        quando necessário. Erros de acesso ao sistema de arquivos são propagados.
    """
    folder = Path(output_directory).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    reports = (
        ("paes.csv", data.paes, ("id_pao", "nome", "preco", "peso_gramas", "categoria")),
        (
            "receitas.csv",
            data.receitas,
            ("pao", "categoria", "ingrediente", "quantidade", "unidade_medida"),
        ),
        ("paes_por_categoria.csv", data.paes_por_categoria, ("categoria", "quantidade")),
        (
            "preco_medio_por_categoria.csv",
            data.preco_medio_por_categoria,
            ("categoria", "preco_medio"),
        ),
        ("uso_ingredientes.csv", data.uso_ingredientes, ("ingrediente", "total_paes")),
    )
    paths = []
    for name, rows, columns in reports:
        path = folder / name
        _write_csv(path, rows, columns)
        paths.append(path)
    return paths
