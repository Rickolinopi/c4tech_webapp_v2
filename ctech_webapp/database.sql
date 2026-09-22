CREATE DATABASE IF NOT EXISTS ctech CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ctech;

CREATE TABLE IF NOT EXISTS users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 cpf VARCHAR(20) NOT NULL UNIQUE,
 email VARCHAR(160) NOT NULL UNIQUE,
 role VARCHAR(80) DEFAULT 'Colaborador',
 password_hash VARCHAR(255) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(150) NOT NULL,
 product_code VARCHAR(60) NOT NULL UNIQUE,
 quantity INT NOT NULL DEFAULT 0,
 image VARCHAR(255),
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
 id INT AUTO_INCREMENT PRIMARY KEY,
 client VARCHAR(150) NOT NULL,
 project VARCHAR(180) NOT NULL,
 machine VARCHAR(150) NOT NULL,
 status ENUM('EM ANDAMENTO','FINALIZADO') NOT NULL DEFAULT 'EM ANDAMENTO',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
 id INT AUTO_INCREMENT PRIMARY KEY,
 order_id INT NOT NULL,
 product_id INT NOT NULL,
 quantity INT NOT NULL,
 FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
 FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT IGNORE INTO users (name,cpf,email,role,password_hash) VALUES
('Administrador','00000000000','admin@ctech.com','Administrador','scrypt:32768:8:1$demo$0a0a0a0a');

INSERT IGNORE INTO products (name,product_code,quantity) VALUES
('Perfil 45x45 LE','PRF-45X45',16),
('Placa POLL','PLACA-POLL',2),
('Parafuso M8','PAR-M8',48);

INSERT IGNORE INTO orders (id,client,project,machine,status) VALUES
(1,'FMC','Isolamento de máquina','Máquina 01','EM ANDAMENTO'),
(2,'SBI','Manutenção','Máquina 02','FINALIZADO');

INSERT IGNORE INTO order_items (order_id,product_id,quantity) VALUES
(1,1,16),(1,2,2),(2,3,8);
