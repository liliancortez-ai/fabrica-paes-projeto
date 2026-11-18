-- Exemplos de consultas SQLite. Execute depois de init-db e seed-demo.

-- 1. Pães e suas categorias.
SELECT p.nome AS pao, c.nome AS categoria, p.preco, p.peso_gramas
FROM pao AS p
LEFT JOIN categoria AS c ON c.id_categoria = p.id_categoria
ORDER BY p.nome;

-- 2. Preço médio por categoria.
SELECT c.nome AS categoria, ROUND(AVG(p.preco), 2) AS preco_medio
FROM categoria AS c
JOIN pao AS p ON p.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nome
ORDER BY c.nome;

-- 3. Ingredientes mais frequentes nas receitas.
SELECT i.nome AS ingrediente, COUNT(DISTINCT pi.id_pao) AS total_paes
FROM ingrediente AS i
JOIN pao_ingrediente AS pi ON pi.id_ingrediente = i.id_ingrediente
GROUP BY i.id_ingrediente, i.nome
ORDER BY total_paes DESC, i.nome;

-- 4. Receitas detalhadas, com unidade de cada ingrediente.
SELECT p.nome AS pao, i.nome AS ingrediente,
       pi.quantidade, i.unidade_medida
FROM pao_ingrediente AS pi
JOIN pao AS p ON p.id_pao = pi.id_pao
JOIN ingrediente AS i ON i.id_ingrediente = pi.id_ingrediente
ORDER BY p.nome, i.nome;

-- 5. Quantos pães existem por categoria.
SELECT COALESCE(c.nome, 'Sem categoria') AS categoria,
       COUNT(*) AS total_paes
FROM pao AS p
LEFT JOIN categoria AS c ON c.id_categoria = p.id_categoria
GROUP BY c.nome
ORDER BY categoria;
