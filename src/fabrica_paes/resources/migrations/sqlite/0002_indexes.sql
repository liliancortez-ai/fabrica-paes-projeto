-- Índices auxiliares de consulta; as chaves primárias já possuem índices próprios.
CREATE INDEX idx_pao_categoria ON pao (id_categoria);
CREATE INDEX idx_pao_ingrediente_ingrediente ON pao_ingrediente (id_ingrediente);
