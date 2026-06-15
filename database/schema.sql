-- ============================================================
--  SCHEMA:  vvt_news
--  PROJETO: Sistema VV&T (login + usuários + notícias)
--
--  Este script cria APENAS a estrutura (banco + tabelas).
--  Para inserir o admin inicial, rode:  python setup_db.py
-- ============================================================

CREATE DATABASE IF NOT EXISTS vvt_news
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE vvt_news;

-- ------------------------------------------------------------
--  TABELA: usuarios
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    senha      VARCHAR(255) NOT NULL,
    tipo       ENUM('admin', 'comum') NOT NULL DEFAULT 'comum',
    ativo      TINYINT(1) NOT NULL DEFAULT 1,
    criado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    editado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
--  TABELA: noticias
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS noticias (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo     VARCHAR(200) NOT NULL,
    data_noticia DATE NOT NULL,
    texto      TEXT NOT NULL,
    imagem     VARCHAR(255) NULL,
    autor_id   INT UNSIGNED NULL,
    ativo      TINYINT(1) NOT NULL DEFAULT 1,
    criado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    editado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_data_noticia (data_noticia),
    INDEX idx_ativo (ativo),
    CONSTRAINT fk_noticias_autor FOREIGN KEY (autor_id)
        REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Pronto! Agora rode:  python setup_db.py
-- Ele vai inserir o usuário admin com hash gerado automaticamente.