"""Testes unitários do interpretador simples de migrações SQL."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fabrica_paes.database import connect

from fabrica_paes.migrations import (Migration, apply_migrations, available_migrations, iter_sql_statements)


class MigrationParserTests(unittest.TestCase):
    """Garante previsibilidade de scripts SQL versionados."""

    def test_multiple_statements_with_comments(self) -> None:
        """Comentários e comandos SQL separados por ponto e vírgula funcionam."""
        statements = list(
            iter_sql_statements("-- comentário\nCREATE TABLE a (id INT);\nCREATE INDEX ix ON a(id);\n")
        )
        self.assertEqual(len(statements), 2)

    def test_modified_applied_migration_is_rejected(self) -> None:
        """Hashes divergentes devem ser detectados sem alterar o histórico."""
        connection = connect(":memory:")
        try:
            apply_migrations(connection)
            original = available_migrations()[0]
            modified = Migration(original.version, original.sql + "-- tampered\n", "0" * 64)
            with patch(
                "fabrica_paes.migrations.available_migrations", return_value=[modified]
            ):
                with self.assertRaisesRegex(ValueError, "foi modificada"):
                    apply_migrations(connection)
        finally:
            connection.close()

    def test_missing_semicolon_raises(self) -> None:
        """Instruções incompletas devem ser explicitamente rejeitadas."""
        with self.assertRaises(ValueError):
            list(iter_sql_statements("CREATE TABLE a (id INT)"))


if __name__ == "__main__":
    unittest.main()
