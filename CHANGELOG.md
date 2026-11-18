# Histórico de alterações

As versões da aplicação seguem [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] — 2026-11-18

### Adicionado
- Aplicação Python instalada via `pyproject.toml` e comando `fabrica-paes`.
- Migrações SQLite incrementais e transacionais, com verificações SHA-256.
- Carga demonstrativa de 4 categorias, 12 pães, 11 ingredientes e 45 composições.
- Relatórios analíticos e exportação de cinco tabelas para CSV.
- Dashboard opcional em Streamlit com filtros e visualizações do projeto.
- Testes unitários, workflow de integração contínua e documentação de arquitetura.
- Scripts SQL de referência para MySQL 8.0+.

### Alterado
- Esquema inicial recebeu validações de integridade, tipos explícitos e índices.

## [0.1.0] — 2026-11-18

### Adicionado
- Modelo relacional inicial em SQLite e MySQL, com tabelas principais e índices.

> Este histórico começa nesta implementação criada a partir do PDF, e não
> representa versões antigas de um código-fonte entregue pelo usuário.
