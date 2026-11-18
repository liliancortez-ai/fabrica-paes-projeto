# Correspondência com o PDF do projeto

Documento-fonte: **Projeto Final — Engenharia da Informação.pdf**, 10 páginas.

| Seção do PDF | Página(s) | Correspondência nesta implementação |
|---|---:|---|
| 2. Análise do Negócio | 3 | Regras de cadastro e composição no modelo ER |
| 3. Modelo Conceitual | 3–4 | Diagrama `docs/architecture.md` e cardinalidades |
| 4. Modelo Lógico | 4–5 | Quatro tabelas e chaves em `resources/migrations/sqlite/0001_initial.sql` |
| 5. Modelo Físico | 5–7 | SQL SQLite operacional e DDL MySQL de referência |
| 6. Base de Dados | 7 | Quatro CSVs demonstrativos com carga idempotente |
| 7. Dashboard BI | 7–9 | `dashboard.py`, `analytics.py`, `export.py` |

## Ajustes explícitos em relação ao texto

- O exemplo SQL do PDF tem declarações `VARCHAR` sem comprimento, `DECIMAL`
  sem precisão e `id_categoria` sem tipo. Os scripts entregues corrigem essas
  lacunas para formar um esquema executável.
- O desenho lógico sugere `preco DECIMAL(8,2)` e `peso_gramas INT`, mantidos
  no DDL de MySQL. Para o SQLite, foi usada afinidade `NUMERIC`.
- Foram adicionadas restrições `CHECK`, nomes únicos, índices e ações
  referenciais. Trata-se de decisões adicionais da implementação, não de
  requisitos textualmente especificados pelo PDF.
- O dashboard no PDF é um **esboço**. O painel desta entrega é funcional e
  usa um conjunto demonstrativo criado aqui; as telas não são reprodução
  pixel a pixel das imagens originais.
- O projeto menciona a possibilidade futura de estoque e produção, mas não
  detalha entidades para esses processos. Assim, nenhuma tabela desse tipo
  foi inventada, e os indicadores são apresentados como **cadastros e receitas**.
