# Git, versões de aplicação e migrações do banco

Há **dois mecanismos de versionamento independentes**:

1. **Código:** Git + tags SemVer `vMAJOR.MINOR.PATCH`, com versão da aplicação
   declarada em `src/fabrica_paes/__init__.py` e lida por `pyproject.toml`.
2. **Banco:** migrações sequenciais `0001_initial.sql`, `0002_indexes.sql`...
   Uma tabela `schema_migrations` grava nome, SHA-256 e data da aplicação.

## Histórico incluído no ZIP

- `v0.1.0`: esquema relacional de partida e índices de consulta.
- `v1.0.0`: código funcional, dados de demonstração, documentação, BI, testes.

**Essas são versões produzidas para esta entrega**, não um histórico recuperado
de arquivos que não foram enviados.

## Comandos Git

```bash
git status
git log --oneline --decorate --graph
git tag --list
git diff v0.1.0..v1.0.0 --stat
```

Para iniciar uma atualização em um repositório hospedado:

```bash
git switch -c feat/minha-melhoria
# modifique e teste os arquivos
git add .
git commit -m "feat: descreve melhoria"
```

Se não precisar manter o histórico local incluído, remova `.git/` e execute
`git init` para criar um repositório novo; porém **não é necessário**.

## Política de migrações

- Nunca edite um arquivo `000N_*.sql` que já foi aplicado em alguma base.
- Para alterar a estrutura, crie um novo script com número superior, por
  exemplo `0003_novo_campo.sql`, e rode `fabrica-paes init-db`.
- A aplicação compara o SHA-256 de cada migração existente com o registrado
  na base. Divergências causam erro explícito antes de prosseguir.
- Cada migração é executada dentro de uma transação SQLite, com `ROLLBACK` em
  caso de falha. Os resultados de `db-status` mostram pendências.
- Os arquivos `sql/mysql` são scripts de referência **sem gerenciamento
  automático de migrações**; não são executados pela CLI.

## Convenção de commits sugerida

- `feat:` nova funcionalidade.
- `fix:` correção de falha.
- `docs:` documentação.
- `test:` testes.
- `refactor:` reorganização sem alteração funcional.
- `chore:` manutenção da estrutura ou do empacotamento.

## Publicação de nova versão

1. Adicione testes da mudança e execute `python -m unittest discover -s tests -v`.
2. Atualize `CHANGELOG.md` e `__version__`.
3. Se alterar o esquema, adicione migração incremental, sem reescrever as antigas.
4. Faça commit e crie uma tag anotada: `git tag -a v1.1.0 -m "Release 1.1.0"`.
