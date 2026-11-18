"""Geração de painel HTML interativo e autônomo a partir de um banco SQLite."""

from __future__ import annotations

import argparse
import json
from contextlib import closing
from importlib.resources import files
from pathlib import Path

from fabrica_paes.database import connect
from fabrica_paes.repository import list_breads, list_categories, list_ingredients, list_recipes


def generate_snapshot(db: str, output: str) -> Path:
    """Gera uma fotografia interativa do catálogo, sem servidor ou rede.

    Args:
        db: Caminho de um SQLite já migrado e carregado.
        output: Arquivo HTML a criar ou sobrescrever; diretórios são criados.

    Returns:
        Caminho do HTML gerado. Os filtros operam sobre os dados incorporados
        no arquivo; execute novamente após alterar o banco de origem.

    Raises:
        sqlite3.Error: Se o banco não contiver o esquema esperado.
        OSError: Se não for possível ler o modelo ou escrever o arquivo.
    """
    with closing(connect(db)) as connection:
        data = {
            "categories": list_categories(connection),
            "ingredients": list_ingredients(connection),
            "breads": list_breads(connection),
            "recipes": list_recipes(connection),
        }
    # Evita que dados do banco terminem prematuramente o elemento script.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    template = files("fabrica_paes").joinpath(
        "resources", "dashboard", "index.html"
    ).read_text(encoding="utf-8")
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(template.replace("__DATA__", payload), encoding="utf-8")
    return destination


def main() -> None:
    """Lê os caminhos na linha de comando e gera o painel HTML autônomo."""
    parser = argparse.ArgumentParser(description="Gera painel HTML autônomo do catálogo.")
    parser.add_argument("--db", required=True, help="Banco SQLite migrado e carregado")
    parser.add_argument("--output", required=True, help="Caminho do HTML de saída")
    args = parser.parse_args()
    print(f"Criado: {generate_snapshot(args.db, args.output)}")


if __name__ == "__main__":
    main()
