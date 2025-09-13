--  Connect to PostgreSQL
psql postgres

-- create demo database
CREATE DATABASE sourcesense_demo;

-- Connect to the demo database
\c sourcesense_demo;

-- Create sample tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    category VARCHAR(100),
    sku VARCHAR(50) UNIQUE
);

-- Insert sample data
INSERT INTO users (email, password_hash, first_name, last_name, phone_number, date_of_birth) VALUES
('john.doe@example.com', 'hashed_password_123', 'John', 'Doe', '+1-555-0123', '1990-05-15'),
('jane.smith@example.com', 'hashed_password_456', 'Jane', 'Smith', '+1-555-0124', '1985-08-22'),
('bob.johnson@example.com', 'hashed_password_789', 'Bob', 'Johnson', '+1-555-0125', '1992-12-10');

INSERT INTO products (name, description, price, category, sku) VALUES
('Laptop Pro', 'High-performance laptop', 1299.99, 'Electronics', 'LAPTOP-001'),
('Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 'Electronics', 'MOUSE-001'),
('Office Chair', 'Comfortable office chair', 199.99, 'Furniture', 'CHAIR-001');

INSERT INTO orders (user_id, order_number, total_amount, status) VALUES
(1, 'ORD-001', 1329.98, 'completed'),
(2, 'ORD-002', 29.99, 'pending'),
(1, 'ORD-003', 199.99, 'shipped');
