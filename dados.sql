-- banco.sql
CREATE DATABASE IF NOT EXISTS protocolodb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE protocolodb;

CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    telefone VARCHAR(20),
    cpf VARCHAR(14),
    foto_perfil TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME DEFAULT NULL 
);

-- Tabela de protocolo
CREATE TABLE protocolo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    nome VARCHAR(255),
    cpf VARCHAR(14),
    email VARCHAR(254),
    telefone VARCHAR(20),
    descricao TEXT,
    estado VARCHAR(50) DEFAULT "Analisando",
    cor VARCHAR(20) DEFAULT "rgb(248, 51, 84)",
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    id_usuario INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME DEFAULT NULL,
    
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE
);

-- Tabela de imagens associadas a um protocolo
CREATE TABLE imagem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT NOT NULL,
    protocolo_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME DEFAULT NULL,
    
    FOREIGN KEY (protocolo_id) REFERENCES protocolo(id) ON DELETE CASCADE
);


