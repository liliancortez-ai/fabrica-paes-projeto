-- Referência para MySQL 8.0+, equivalente à estrutura operacional em SQLite.
-- Crie um schema separado antes de executar se necessário.
CREATE DATABASE IF NOT EXISTS fabrica_paes
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fabrica_paes;

CREATE TABLE categoria (
    id_categoria INT PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE pao (
    id_pao INT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    preco DECIMAL(8,2) NOT NULL,
    peso_gramas INT NOT NULL,
    id_categoria INT NULL,
    CONSTRAINT chk_pao_preco CHECK (preco >= 0),
    CONSTRAINT chk_pao_peso CHECK (peso_gramas > 0),
    CONSTRAINT fk_pao_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria (id_categoria)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE ingrediente (
    id_ingrediente INT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    unidade_medida VARCHAR(20) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE pao_ingrediente (
    id_pao INT NOT NULL,
    id_ingrediente INT NOT NULL,
    quantidade DECIMAL(12,3) NOT NULL,
    PRIMARY KEY (id_pao, id_ingrediente),
    CONSTRAINT chk_receita_quantidade CHECK (quantidade > 0),
    CONSTRAINT fk_receita_pao FOREIGN KEY (id_pao)
        REFERENCES pao (id_pao)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_receita_ingrediente FOREIGN KEY (id_ingrediente)
        REFERENCES ingrediente (id_ingrediente)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;
