# Fábrica de Pães — Engenharia da Informação

[![Testes](https://img.shields.io/badge/testes-unittest-blue)](#testes)

Projeto **executável e versionado** baseado no trabalho *Projeto Final — Modelagem
de Banco de Dados para Gestão de uma Fábrica de Pães* (UFOP, 2026).

O modelo abrange **CATEGORIA, PAO, INGREDIENTE e PAO_INGREDIENTE**;
a tabela associativa registra a quantidade de cada ingrediente por receita.
Foram incluídos migrações, dados demonstrativos, relatórios CSV, testes e um
painel BI opcional em Streamlit. A implementação usa **Python + SQLite** para
funcionar localmente sem servidor. A pasta `sql/mysql` contém a versão do DDL
para MySQL 8.0+, compatível com a proposta do texto original.

> **Escopo:** o banco modela produtos e receitas, não registra ordens de produção,
> estoque, compras nem vendas. Os indicadores não representam produção real.
> Os CSVs são uma **reconstrução demonstrativa**, não a planilha original do PDF.

## Instalação e execução

Requisitos: **Python 3.10+**. Rode os comandos a partir da raiz do projeto.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .

fabrica-paes init-db
fabrica-paes seed-demo
fabrica-paes report
fabrica-paes db-status
fabrica-paes export-csv --output exports
```

Exemplo da saída do relatório após a carga demonstrativa:

```text
Pães cadastrados: 12
Ingredientes distintos nas receitas: 11
Preço médio (R$): 4.82
Peso médio (g): 253
Linhas de receitas: 45
```

Para usar outro arquivo SQLite, defina a variável de ambiente `FABRICA_PAES_DB`
ou coloque `--db CAMINHO` **antes do subcomando**:

```bash
fabrica-paes --db data-local/minha-fabrica.sqlite3 init-db
fabrica-paes --db data-local/minha-fabrica.sqlite3 seed-demo
fabrica-paes --db data-local/minha-fabrica.sqlite3 report
```

O comando também pode ser invocado por `python -m fabrica_paes`.

## Resultados gerados

Abra [o dashboard HTML](resultados/dashboard.html) diretamente no navegador.
Ele apresenta uma fotografia interativa da carga simulada, com filtros, análise de ingredientes por receita e busca, sem instalação adicional. Regenere o HTML quando os dados mudarem.
Os [resultados e instruções de reprodução](resultados/README.md) incluem os
indicadores e os CSVs para planilhas. Para explorar filtros, use o painel
interativo abaixo.

## Dashboard BI opcional

```bash
python -m pip install -e ".[dashboard]"
fabrica-paes init-db
fabrica-paes seed-demo
streamlit run src/fabrica_paes/dashboard.py
```

O dashboard apresenta filtros por categoria, pão e ingrediente; KPIs de
cadastros, preço e peso médio; preços por pão e categoria; frequência de
ingredientes; e uma tabela das receitas com quantidade e unidade. Ao filtrar
por ingrediente, são selecionados os pães que o utilizam, mas a composição
exibida é **completa** para os produtos selecionados.

O [guia dos scripts](docs/scripts.md) descreve os módulos e arquivos SQL, incluindo os cuidados com migrações versionadas.

## Estrutura de diretórios

```text
fabrica-paes-projeto/
├── .git/                       Histórico Git com tags v0.1.0 e v1.0.0
├── .github/workflows/          Testes automáticos no GitHub Actions
├── docs/
│   ├── architecture.md         Camadas, modelo ER e decisões técnicas
│   ├── data_dictionary.md      Campos, tipos e regras de negócio
│   ├── source_alignment.md     Relação com as seções do PDF
│   └── versioning.md           Convenções de versões, migrações e Git
├── examples/queries.sql        Consultas analíticas de exemplo (SQLite)
├── sql/mysql/                  Esquema e índices de referência para MySQL
├── src/fabrica_paes/
│   ├── analytics.py            Cálculo dos indicadores e filtros
│   ├── cli.py                  Interface de linha de comando
│   ├── config.py               Configuração e caminhos
│   ├── dashboard.py            Interface Streamlit (extra opcional)
│   ├── database.py             Conexão SQLite e PRAGMAs
│   ├── export.py               Exportação para CSV
│   ├── migrations.py           Migrações transacionais com SHA-256
│   ├── repository.py           Consultas SQL parametrizadas
│   ├── seed.py                 Importação idempotente dos CSVs
│   └── resources/
│       ├── migrations/sqlite/  0001_initial.sql, 0002_indexes.sql
│       └── seed/               Categorias, pães, ingredientes e receitas
├── tests/                      Testes unitários e de integração
├── CHANGELOG.md                Registro das alterações por versão
└── pyproject.toml              Metadados, empacotamento e dependências
```

**Por que `resources` fica dentro de `src/fabrica_paes`?** Porque os arquivos
SQL e CSV são empacotados junto com o Python: instalações por `pip` não perdem
os dados de exemplo nem as migrações.

## Testes

```bash
python -m unittest discover -s tests -v
```

Testam chaves estrangeiras, restrições de quantidade e preço, idempotência
na carga, filtros BI, migrações repetidas, comportamento da CLI e exportação.
As suítes utilizam bancos isolados em memória/temporários e não alteram a
base que você inicializou para experimentar.

## Versionamento

O ZIP inclui a pasta `.git`, isto é, **histórico Git real**, não somente
arquivos de texto sobre versões. Para consultar:

```bash
git log --oneline --decorate
git tag --list
git show v0.1.0
git show v1.0.0
```

As versões seguem **SemVer** (`MAJOR.MINOR.PATCH`) e o estado de cada banco
é controlado, separadamente, por migrações `0001_...sql`, `0002_...sql`.
Os scripts já aplicados têm seu SHA-256 registrado, e mudanças posteriores
nesses scripts causam erro intencional. Leia [docs/versioning.md](docs/versioning.md).

## Organização dos dados e do MySQL

O SQLite gerado **não é enviado ao Git** (veja `.gitignore`). Isso mantém o
repositório reproduzível: versão-se código, scripts de migração e entradas
CSV, não o estado mutável de cada instalação. Em MySQL, use
`sql/mysql/0001_initial.sql` e depois `sql/mysql/0002_indexes.sql` no cliente
SQL; o dashboard e a CLI atuais executam **somente em SQLite**.

O script SQL mostrado no PDF apresenta campos sem tipo ou largura e por isso
não pode ser executado literalmente em alguns SGBDs. Os scripts desta entrega
explicitam tipos e restrições, preservando a estrutura de quatro tabelas.

## Licenciamento e proveniência

Implementação nova criada a partir da **descrição, modelagem e imagens** do PDF,
sem pressupor acesso aos arquivos-fonte originais. Não é uma edição de um
repositório preexistente. Consulte o responsável pelo projeto antes de
publicar ou reutilizar conteúdos acadêmicos de terceiros.
