-- Script de inicialización para Tienda el Regalito POS

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Cajero', -- Cajero, Admin
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    barcode VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    current_stock INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER NOT NULL DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cash_registers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    opening_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    opening_amount DECIMAL(10, 2) NOT NULL,
    petty_cash DECIMAL(10, 2) NOT NULL DEFAULT 0,
    closing_time TIMESTAMP,
    blind_closing_amount DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'Abierta' -- Abierta, Cerrada
);

-- Insertar usuario Admin por defecto (contraseña: admin123)
-- Hash generado con bcrypt para 'admin123'
INSERT INTO users (username, password_hash, role) VALUES 
('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin');

-- Insertar algunos productos de prueba
INSERT INTO products (name, barcode, price, current_stock, min_stock) VALUES 
('Refresco Cola 600ml', '7501055300075', 18.50, 50, 10),
('Papas Fritas', '7501000123456', 22.00, 30, 5),
('Galletas de Chocolate', '7501000987654', 15.00, 20, 5);
