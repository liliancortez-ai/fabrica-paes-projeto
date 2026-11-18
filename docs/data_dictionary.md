# Dicionário de dados

## `categoria`

| Campo | SQLite | MySQL | Regra |
|---|---|---|---|
| `id_categoria` | INTEGER | INT | Chave primária |
| `nome` | TEXT | VARCHAR(80) | Não nulo e único |

## `pao`

| Campo | SQLite | MySQL | Regra |
|---|---|---|---|
| `id_pao` | INTEGER | INT | Chave primária |
| `nome` | TEXT | VARCHAR(120) | Não nulo e único |
| `preco` | NUMERIC | DECIMAL(8,2) | Não negativo, moeda BRL |
| `peso_gramas` | INTEGER | INT | Estritamente positivo, g |
| `id_categoria` | INTEGER | INT | FK opcional `categoria` |

Uma categoria excluída deixa os pães existentes sem categoria
(`ON DELETE SET NULL`), sem excluir os produtos.

## `ingrediente`

| Campo | SQLite | MySQL | Regra |
|---|---|---|---|
| `id_ingrediente` | INTEGER | INT | Chave primária |
| `nome` | TEXT | VARCHAR(120) | Não nulo e único |
| `unidade_medida` | TEXT | VARCHAR(20) | Não nulo; valores do exemplo: kg, g, L, ml |

## `pao_ingrediente`

| Campo | SQLite | MySQL | Regra |
|---|---|---|---|
| `id_pao` | INTEGER | INT | PK composta + FK para `pao` |
| `id_ingrediente` | INTEGER | INT | PK composta + FK para `ingrediente` |
| `quantidade` | NUMERIC | DECIMAL(12,3) | Positiva; unidade vem de `ingrediente` |

Excluir um pão exclui suas linhas de composição (`CASCADE`). Excluir um
ingrediente ainda utilizado em uma receita é bloqueado (`RESTRICT`).

## Dicionário dos indicadores

| Indicador | Definição |
|---|---|
| Pães cadastrados | Quantidade de registros `pao` no filtro |
| Ingredientes distintos | Número de IDs de ingrediente presentes nas receitas dos pães filtrados |
| Preço médio | Média dos preços cadastrados dos pães filtrados, em reais |
| Peso médio | Média de `peso_gramas` dos pães filtrados |
| Pães por categoria | Contagem de pães por nome de categoria |
| Uso de ingredientes | Quantidade de pães cuja receita inclui um ingrediente |
| Linhas de receita | Contagem de pares `(id_pao, id_ingrediente)` nos filtros |

A quantidade de ingrediente é armazenada na unidade definida no cadastro.
**Não** se deve somar quantidades de ingredientes diferentes ou de unidades
diferentes e interpretar essa soma como massa total.

## Dataset demonstrativo

Arquivos CSV em `src/fabrica_paes/resources/seed/`:

| Arquivo | Linhas de dados | Conteúdo |
|---|---:|---|
| `categorias.csv` | 4 | Tradicional, Doce, Integral, Especial |
| `paes.csv` | 12 | Produtos, preços, pesos, categorias |
| `ingredientes.csv` | 11 | Ingredientes e unidades |
| `receitas.csv` | 45 | Vinculação de pães com ingredientes |

Os exemplos foram **construídos** para esta implementação. Os totais 12, 11,
45, R$ 4,82 e 253 g reproduzem os indicadores agregados visíveis nas figuras
do PDF, sem afirmar que os registros ou receitas individuais sejam idênticos
à planilha que deu origem ao trabalho.
