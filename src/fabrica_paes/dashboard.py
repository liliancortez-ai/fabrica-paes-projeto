"""Dashboard BI em Streamlit com filtros consistentes e receitas completas.

Uso (após instalar o extra opcional):
    streamlit run src/fabrica_paes/dashboard.py

Não representa dados efetivos de produção, vendas ou estoque: o banco contém
somente produtos, categorias, ingredientes e composições de receitas.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing

import streamlit as st

from fabrica_paes.analytics import build_dashboard
from fabrica_paes.database import connect
from fabrica_paes.repository import list_breads, list_categories, list_ingredients


def _currency(value: object) -> str:
    """Converte um número para apresentação em reais com duas casas decimais.

    Args:
        value: Valor conversível para ``float``.

    Returns:
        Texto com vírgula decimal e ponto como separador de milhares.
    """
    numeric = float(value)
    return f"R$ {numeric:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")


def render() -> None:
    """Abre o banco configurado e apresenta a visão interativa em Streamlit.

    Os filtros são combinados por interseção e usam ``build_dashboard``;
    selecionar um ingrediente mantém completas as receitas dos pães
    correspondentes. O arquivo SQLite é fechado após a leitura. Se o esquema
    estiver indisponível, exibe uma mensagem e instruções de inicialização.
    """
    st.set_page_config(page_title="Fábrica de Pães | BI", layout="wide")
    st.title("Fábrica de Pães — Dashboard BI")
    st.caption(
        "Indicadores de cadastro e composição de receitas. "
        "Os dados de demonstração são simulados."
    )

    try:
        with closing(connect()) as connection:
            categories = list_categories(connection)
            breads = list_breads(connection)
            ingredients = list_ingredients(connection)
            category_options = {"Todas as categorias": None}
            category_options.update({item["nome"]: item["id_categoria"] for item in categories})
            bread_options = {"Todos os pães": None}
            bread_options.update({item["nome"]: item["id_pao"] for item in breads})
            ingredient_options = {"Todos os ingredientes": None}
            ingredient_options.update(
                {item["nome"]: item["id_ingrediente"] for item in ingredients}
            )
            first, second, third = st.columns(3)
            with first:
                category_name = st.selectbox("Categoria", list(category_options))
            with second:
                bread_name = st.selectbox("Pão", list(bread_options))
            with third:
                ingredient_name = st.selectbox("Ingrediente", list(ingredient_options))

            data = build_dashboard(
                connection,
                categoria_id=category_options[category_name],
                pao_id=bread_options[bread_name],
                ingrediente_id=ingredient_options[ingredient_name],
            )
    except sqlite3.Error as error:
        st.error(f"Banco não inicializado ou inacessível: {error}")
        st.code("fabrica-paes init-db\nfabrica-paes seed-demo", language="bash")
        return

    a, b, c, d = st.columns(4)
    a.metric("Pães cadastrados", data.total_paes)
    b.metric("Preço médio", _currency(data.preco_medio))
    c.metric("Peso médio", f"{data.peso_medio_gramas:.0f} g")
    d.metric("Ingredientes distintos", data.total_ingredientes)
    st.caption(f"{data.total_linhas_receitas} linhas de composições de receitas no filtro atual.")

    if not data.total_paes:
        st.info("Nenhum pão corresponde aos filtros selecionados.")
        return

    left, right = st.columns(2)
    with left:
        st.subheader("Preço por pão (R$)")
        st.bar_chart(data.paes, x="nome", y="preco")
        st.subheader("Pães por categoria")
        st.bar_chart(data.paes_por_categoria, x="categoria", y="quantidade")
    with right:
        st.subheader("Uso de ingredientes (número de pães)")
        st.bar_chart(data.uso_ingredientes, x="ingrediente", y="total_paes")
        st.subheader("Preço médio por categoria (R$)")
        st.bar_chart(data.preco_medio_por_categoria, x="categoria", y="preco_medio")

    st.subheader("Composição das receitas")
    st.dataframe(
        [
            {
                "Pão": row["pao"],
                "Categoria": row["categoria"],
                "Ingrediente": row["ingrediente"],
                "Quantidade": row["quantidade"],
                "Unidade": row["unidade_medida"],
            }
            for row in data.receitas
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Ao filtrar por ingrediente, o painel seleciona os pães que o utilizam "
        "e exibe a receita completa desses produtos."
    )


if __name__ == "__main__":
    render()
