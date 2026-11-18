"""Interface de linha de comando para banco, relatórios e exportação."""

from __future__ import annotations

import argparse
from contextlib import closing
import sqlite3
import sys
from typing import Sequence

from fabrica_paes import __version__
from fabrica_paes.analytics import build_dashboard
from fabrica_paes.database import connect
from fabrica_paes.export import export_reports
from fabrica_paes.migrations import apply_migrations, migration_status
from fabrica_paes.seed import seed_demo


def create_parser() -> argparse.ArgumentParser:
    """Constrói o analisador dos comandos e filtros de linha de comando.

    O caminho global ``--db`` deve preceder o subcomando. Os filtros de
    relatório e exportação recebem IDs inteiros; a interpretação é feita por
    ``build_dashboard``. Retorna um parser pronto para ``parse_args``.
    """
    parser = argparse.ArgumentParser(
        prog="fabrica-paes",
        description="Fábrica de Pães: migrações, dados demonstrativos e BI.",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Caminho do banco SQLite; padrão: FABRICA_PAES_DB ou ./fabrica_paes.sqlite3",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init-db", help="Cria/atualiza o esquema aplicando migrações pendentes")
    commands.add_parser("seed-demo", help="Carrega dados de demonstração de maneira idempotente")
    commands.add_parser("db-status", help="Exibe estado das migrações do banco")

    report = commands.add_parser("report", help="Mostra indicadores e contagens no terminal")
    export = commands.add_parser("export-csv", help="Exporta tabelas e indicadores em CSV")
    export.add_argument("--output", default="exports", help="Diretório de saída, padrão: exports")
    for command in (report, export):
        command.add_argument("--category", type=int, default=None, help="ID da categoria")
        command.add_argument("--bread", type=int, default=None, help="ID do pão")
        command.add_argument("--ingredient", type=int, default=None, help="ID do ingrediente")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    """Executa um subcomando e retorna um código de saída convencional.

    Args:
        argv: Argumentos sem o nome do executável; ``None`` usa ``sys.argv``.

    Returns:
        ``0`` em caso de sucesso, ``1`` em erro operacional. Argumentos
        inválidos são tratados pelo argparse, que encerra com código 2.

    Notes:
        Abre e fecha sua própria conexão. Erros de banco, validação e arquivo
        são apresentados em stderr, sem traceback para erros esperados.
    """
    args = create_parser().parse_args(argv)
    try:
        with closing(connect(args.db)) as connection:
            if args.command == "init-db":
                applied = apply_migrations(connection)
                if applied:
                    print("Migrações aplicadas:", ", ".join(applied))
                else:
                    print("Banco atualizado: nenhuma migração pendente.")
                return 0
            if args.command == "db-status":
                for migration in migration_status(connection):
                    flag = "OK" if migration["aplicada"] and migration["checksum_valido"] else (
                        "ALTERADA" if migration["aplicada"] else "PENDENTE"
                    )
                    print(f"{migration['versao']}: {flag}")
                return 0
            if args.command == "seed-demo":
                counts = seed_demo(connection)
                print("Carga demonstrativa aplicada:")
                for table, count in counts.items():
                    print(f"  {table}: {count} registros lidos")
                return 0
            data = build_dashboard(
                connection,
                categoria_id=args.category,
                pao_id=args.bread,
                ingrediente_id=args.ingredient,
            )
            if args.command == "report":
                print(f"Pães cadastrados: {data.total_paes}")
                print(f"Ingredientes distintos nas receitas: {data.total_ingredientes}")
                print(f"Preço médio (R$): {data.preco_medio:.2f}")
                print(f"Peso médio (g): {data.peso_medio_gramas:.0f}")
                print(f"Linhas de receitas: {data.total_linhas_receitas}")
                return 0
            if args.command == "export-csv":
                for path in export_reports(data, args.output):
                    print(f"Criado: {path}")
                return 0
    except (sqlite3.Error, ValueError, RuntimeError, OSError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        print("Dica: execute 'fabrica-paes init-db' antes da carga e dos relatórios.", file=sys.stderr)
        return 1
    return 1


def main() -> None:
    """Executa a CLI instalada e encerra o processo com o código de ``run``."""
    raise SystemExit(run())
