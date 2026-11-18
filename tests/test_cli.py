"""Testes end-to-end da interface de linha de comando."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from fabrica_paes.cli import run


class CommandLineTests(unittest.TestCase):
    """Executa a CLI sem depender de processos ou dados reais externos."""

    def test_full_lifecycle(self) -> None:
        """Migração, carga, relatório e exportação devem funcionar em sequência."""
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "db.sqlite3")
            output = str(Path(directory) / "exports")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(run(["--db", database, "init-db"]), 0)
                self.assertEqual(run(["--db", database, "seed-demo"]), 0)
                self.assertEqual(run(["--db", database, "report"]), 0)
                self.assertEqual(
                    run(["--db", database, "export-csv", "--output", output]), 0
                )
                self.assertEqual(run(["--db", database, "db-status"]), 0)
            self.assertIn("Preço médio (R$): 4.82", stdout.getvalue())
            self.assertIn("0001_initial: OK", stdout.getvalue())
            self.assertTrue((Path(output) / "receitas.csv").is_file())

    def test_report_without_migration_fails_cleanly(self) -> None:
        """Banco sem estrutura deve apresentar erro tratável, não traceback."""
        with tempfile.TemporaryDirectory() as directory:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = run(["--db", str(Path(directory) / "new.db"), "report"])
            self.assertEqual(exit_code, 1)
            self.assertIn("init-db", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
