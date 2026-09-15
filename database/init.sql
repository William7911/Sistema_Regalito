-- Script de inicialización para Tienda el Regalito POS
-- Ejecuta SOLO la primera vez que se levanta el contenedor (volumen vacío).

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    code VARCHAR(30) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) UNIQUE,
    barcode VARCHAR(100) UNIQUE NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
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

-- Roles por defecto
INSERT INTO roles (name, description) VALUES
('Admin', 'Administrador del sistema'),
('Cajero', 'Operador de caja');

-- Departamentos por defecto
INSERT INTO departments (name, description) VALUES
('General', 'Departamento general');

-- Insertar usuario Admin por defecto (contraseña: admin123)
INSERT INTO users (name, lastname, code, username, password_hash, role_id, department_id) VALUES
('Admin', 'Sistema', 'U001', 'admin',
 '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
 (SELECT id FROM roles WHERE name = 'Admin'),
 (SELECT id FROM departments WHERE name = 'General'));

-- Insertar categorías de prueba
INSERT INTO categories (name, description) VALUES
('Bebidas', 'Refrescos, jugos y aguas'),
('Snacks', 'Botanas y frituras'),
('Dulcería', 'Galletas, dulces y chocolates');

-- Insertar algunos productos de prueba (vinculados a categorías 1, 2 y 3)
INSERT INTO products (name, sku, barcode, category_id, price, current_stock, min_stock) VALUES
('Refresco Cola 600ml', 'COLA600', '7501055300075', 1, 18.50, 50, 10),
('Papas Fritas', 'PAPA22',   '7501000123456', 2, 22.00, 30, 5),
('Galletas de Chocolate', 'GALLC40', '7501000987654', 3, 15.00, 20, 5);