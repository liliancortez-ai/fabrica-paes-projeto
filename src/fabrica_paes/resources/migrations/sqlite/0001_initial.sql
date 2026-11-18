-- Modelo relacional inicial: projeto de gestão da fábrica de pães.
-- SQLite; migrado pela aplicação, nunca executado como script solto.
CREATE TABLE categoria (
    id_categoria INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE CHECK (length(trim(nome)) > 0)
);

CREATE TABLE pao (
    id_pao INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE CHECK (length(trim(nome)) > 0),
    preco NUMERIC NOT NULL CHECK (preco >= 0),
    peso_gramas INTEGER NOT NULL CHECK (peso_gramas > 0),
    id_categoria INTEGER,
    FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE ingrediente (
    id_ingrediente INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE CHECK (length(trim(nome)) > 0),
    unidade_medida TEXT NOT NULL CHECK (length(trim(unidade_medida)) > 0)
);

CREATE TABLE pao_ingrediente (
    id_pao INTEGER NOT NULL,
    id_ingrediente INTEGER NOT NULL,
    quantidade NUMERIC NOT NULL CHECK (quantidade > 0),
    PRIMARY KEY (id_pao, id_ingrediente),
    FOREIGN KEY (id_pao) REFERENCES pao (id_pao)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_ingrediente) REFERENCES ingrediente (id_ingrediente)
        ON UPDATE CASCADE ON DELETE RESTRICT
);
