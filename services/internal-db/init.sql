CREATE DATABASE IF NOT EXISTS secrets;

USE secrets;

CREATE TABLE IF NOT EXISTS flag (
    id INT PRIMARY KEY,
    value VARCHAR(255) NOT NULL
);

INSERT INTO flag (id, value) VALUES (1, 'FLAG{infiltration_success}');

CREATE TABLE IF NOT EXISTS credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service VARCHAR(100),
    username VARCHAR(100),
    password VARCHAR(255)
);

INSERT INTO credentials (service, username, password) VALUES
('internal-api', 'admin', 's3cret-internal-key-2024'),
('ssh-server', 'admin', 'admin123'),
('ftp-server', 'admin', 'admin123');
