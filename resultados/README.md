# Resultados da carga demonstrativa

Os registros são simulados e reconstruídos para demonstrar o modelo do PDF; não são a planilha original nem medições da fábrica. Abra `dashboard.html` no navegador para visualizar os indicadores e as 45 relações entre pães e ingredientes. A pasta `csv` contém as tabelas e agregações para análise em planilha (UTF-8 com BOM e separador `;`).

| Indicador | Resultado |
|---|---:|
| Pães cadastrados | 12 |
| Ingredientes distintos usados nas receitas | 11 |
| Preço médio por pão | R$ 4,82 |
| Peso médio por pão | 253 g |
| Relações pão–ingrediente | 45 |

As quatro categorias — Doce, Especial, Integral e Tradicional — têm três pães cada. Farinha de Trigo aparece em 12 pães; Fermento Biológico e Água, em 8 cada. Essas frequências contam pães distintos, não quantidade consumida. O preço médio é a média simples dos preços cadastrados, sem ponderação por vendas.

Para recriar o banco, CSVs e painel a partir da raiz do projeto, com Python 3.10 ou superior:

```bash
PYTHONPATH=src python -m fabrica_paes --db resultados/fabrica_paes.sqlite3 init-db
PYTHONPATH=src python -m fabrica_paes --db resultados/fabrica_paes.sqlite3 seed-demo
PYTHONPATH=src python -m fabrica_paes --db resultados/fabrica_paes.sqlite3 export-csv --output resultados/csv
PYTHONPATH=src python -m fabrica_paes.snapshot --db resultados/fabrica_paes.sqlite3 --output resultados/dashboard.html
```

O HTML é uma fotografia do banco com filtros interativos locais: regenere-o após alterações na base. Os filtros de categoria, pão e ingrediente combinam-se por interseção; a busca restringe apenas a tabela de receitas. Para acesso direto ao banco e filtros atualizados, use também o painel Streamlit descrito no README principal. O arquivo SQLite gerado é local e ignorado pelo Git.
