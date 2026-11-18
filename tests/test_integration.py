"""Testes integrados das migrações, dos dados, dos indicadores e dos relatórios."""

from __future__ import annotations

import csv
import sqlite3
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fabrica_paes.analytics import build_dashboard
from fabrica_paes.database import connect
from fabrica_paes.export import export_reports
from fabrica_paes.migrations import apply_migrations, migration_status
from fabrica_paes.seed import seed_demo


class DatabaseIntegrationTests(unittest.TestCase):
    """Valida invariantes relacionais sobre um banco isolado por teste."""

    def setUp(self) -> None:
        """Inicia uma base em memória com os dois scripts de migração."""
        self.connection = connect(":memory:")
        self.assertEqual(len(apply_migrations(self.connection)), 2)

    def tearDown(self) -> None:
        """Libera a conexão ao encerrar o teste."""
        self.connection.close()

    def test_migrations_are_idempotent_and_checksums_are_valid(self) -> None:
        """Rodar as migrações novamente não deve recriar objetos."""
        self.assertEqual(apply_migrations(self.connection), [])
        status = migration_status(self.connection)
        self.assertTrue(all(item["aplicada"] for item in status))
        self.assertTrue(all(item["checksum_valido"] for item in status))

    def test_seed_is_idempotent_and_matches_dashboard_aggregates(self) -> None:
        """A carga demo preserva as quantidades e médias ilustrativas."""
        first = seed_demo(self.connection)
        second = seed_demo(self.connection)
        expected = {"categoria": 4, "ingrediente": 11, "pao": 12, "pao_ingrediente": 45}
        self.assertEqual(first, expected)
        self.assertEqual(second, expected)
        dashboard = build_dashboard(self.connection)
        self.assertEqual(dashboard.total_paes, 12)
        self.assertEqual(dashboard.total_ingredientes, 11)
        self.assertEqual(dashboard.total_linhas_receitas, 45)
        self.assertEqual(dashboard.preco_medio, Decimal("4.82"))
        self.assertEqual(dashboard.peso_medio_gramas, Decimal("253"))

    def test_constraints_and_foreign_keys(self) -> None:
        """O schema proíbe preços negativos, quantidades zero e FKs órfãs."""
        seed_demo(self.connection)
        self.assertEqual(self.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO pao (id_pao, nome, preco, peso_gramas) VALUES (99, 'Invalido', -1, 100)"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO pao_ingrediente VALUES (1, 1000, 2)"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO pao_ingrediente VALUES (1, 1, 0)"
            )
        self.connection.rollback()

    def test_category_filter_and_ingredient_filter(self) -> None:
        """Filtros preservam a regra de receitas completas dos pães elegíveis."""
        seed_demo(self.connection)
        traditional = build_dashboard(self.connection, categoria_id=1)
        self.assertEqual(traditional.total_paes, 3)
        self.assertTrue(all(b["categoria"] == "Tradicional" for b in traditional.paes))
        ingredient = build_dashboard(self.connection, ingrediente_id=11)
        self.assertEqual(ingredient.total_paes, 1)
        self.assertEqual(ingredient.paes[0]["nome"], "Pão de Milho")
        self.assertEqual(len(ingredient.receitas), 3)
        empty = build_dashboard(self.connection, categoria_id=1, ingrediente_id=11)
        self.assertEqual(empty.total_paes, 0)
        self.assertEqual(empty.total_ingredientes, 0)
        self.assertEqual(empty.preco_medio, Decimal("0.00"))

    def test_csv_exports(self) -> None:
        """Os cinco CSVs devem ser gerados e conter os cabeçalhos esperados."""
        seed_demo(self.connection)
        with tempfile.TemporaryDirectory() as directory:
            paths = export_reports(build_dashboard(self.connection), directory)
            self.assertEqual(len(paths), 5)
            for path in paths:
                self.assertTrue(path.is_file())
            with (Path(directory) / "receitas.csv").open(
                "r", encoding="utf-8-sig", newline=""
            ) as file:
                rows = list(csv.DictReader(file, delimiter=";"))
            self.assertEqual(len(rows), 45)
            self.assertEqual(
                list(rows[0]), ["pao", "categoria", "ingrediente", "quantidade", "unidade_medida"]
            )

    def test_delete_pao_cascades_only_recipe_links(self) -> None:
        """Apagar um produto apaga a composição, não o ingrediente global."""
        seed_demo(self.connection)
        before = self.connection.execute("SELECT COUNT(*) FROM ingrediente").fetchone()[0]
        self.connection.execute("DELETE FROM pao WHERE id_pao = 1")
        self.assertEqual(
            self.connection.execute(
                "SELECT COUNT(*) FROM pao_ingrediente WHERE id_pao = 1"
            ).fetchone()[0],
            0,
        )
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM ingrediente").fetchone()[0], before)


if __name__ == "__main__":
    unittest.main()
