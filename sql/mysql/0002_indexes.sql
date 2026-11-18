-- Índices sugeridos para MySQL; execute após 0001_initial.sql.
-- A FK em InnoDB pode criar índices de suporte automaticamente.
CREATE INDEX idx_pao_categoria ON pao (id_categoria);
CREATE INDEX idx_receita_ingrediente ON pao_ingrediente (id_ingrediente);
