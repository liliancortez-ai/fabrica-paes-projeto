# Guia dos scripts e recursos executáveis

Os módulos Python em `src/fabrica_paes` incluem docstrings de suas funções e classes. O pacote separa configuração (`config`), conexão (`database`), migrações (`migrations`), carga (`seed`), consultas (`repository`), indicadores (`analytics`), exportação (`export`), comandos (`cli`) e interfaces (`dashboard` e `snapshot`). A interface Streamlit consulta o banco ao executar; `snapshot` incorpora os registros num HTML autônomo, que deve ser regenerado após mudanças na base. O modelo HTML em `resources/dashboard/index.html` contém os estilos, as interações e as fórmulas do painel; comentários junto às funções JavaScript descrevem seus papéis.

## SQL

- `resources/migrations/sqlite/0001_initial.sql`: cria as quatro tabelas do modelo, chaves e restrições de integridade para produtos e receitas. É a primeira migração da aplicação.
- `resources/migrations/sqlite/0002_indexes.sql`: cria índices para buscas de pães por categoria e de receitas por ingrediente, além dos índices das chaves primárias.
- `sql/mysql/0001_initial.sql`: implementa o esquema equivalente para MySQL; destina-se à execução manual no servidor MySQL, não à CLI SQLite.
- `sql/mysql/0002_indexes.sql`: adiciona índices para consultas por categoria e ingrediente após a criação do esquema MySQL.
- `examples/queries.sql`: contém consultas SQLite independentes para catálogo, média por categoria, frequência de ingredientes, receitas e distribuição de pães. Execute após inicializar e carregar a base; as consultas apenas leem os dados.

Os arquivos de migração SQLite já aplicados não devem ser editados, nem mesmo para acrescentar comentários: seu conteúdo é conferido pelo SHA-256 salvo no banco. Mudanças no esquema exigem uma nova migração versionada. As entradas CSV em `resources/seed` são dados demonstrativos, não scripts nem dados reais da fábrica.
