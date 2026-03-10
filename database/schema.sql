USE QuoteProDB;
GO

-- CATEGORIAS
CREATE TABLE categories (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    name        NVARCHAR(100) NOT NULL,
    description NVARCHAR(500) NULL,
    is_active   BIT DEFAULT 1,
    created_at  DATETIME DEFAULT GETDATE()
);
GO

-- PROVEEDORES
CREATE TABLE providers (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    code            NVARCHAR(20) NOT NULL UNIQUE,
    name            NVARCHAR(200) NOT NULL,
    contact_name    NVARCHAR(200) NULL,
    email           NVARCHAR(200) NULL,
    phone           NVARCHAR(50) NULL,
    address         NVARCHAR(500) NULL,
    nit             NVARCHAR(50) NULL,
    payment_terms   INT DEFAULT 30,
    delivery_days   INT DEFAULT 1,
    is_active       BIT DEFAULT 1,
    created_at      DATETIME DEFAULT GETDATE()
);
GO

-- PRODUCTOS
CREATE TABLE products (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    code            NVARCHAR(50) NOT NULL UNIQUE,
    name            NVARCHAR(200) NOT NULL,
    description     NVARCHAR(1000) NULL,
    unit            NVARCHAR(30) DEFAULT 'UND',
    category_id     INT NULL REFERENCES categories(id),
    brand           NVARCHAR(100) NULL,
    is_active       BIT DEFAULT 1,
    created_at      DATETIME DEFAULT GETDATE()
);
GO

-- PRECIOS POR PROVEEDOR
CREATE TABLE product_prices (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    product_id      INT NOT NULL REFERENCES products(id),
    provider_id     INT NOT NULL REFERENCES providers(id),
    price           DECIMAL(18,2) NOT NULL,
    tax_percent     DECIMAL(5,2) DEFAULT 19.0,
    is_active       BIT DEFAULT 1,
    updated_at      DATETIME DEFAULT GETDATE()
);
GO

-- COTIZACIONES
CREATE TABLE quotes (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    quote_number    NVARCHAR(20) NOT NULL UNIQUE,
    client_name     NVARCHAR(200) NOT NULL,
    client_email    NVARCHAR(200) NULL,
    client_phone    NVARCHAR(50) NULL,
    notes           NVARCHAR(1000) NULL,
    total_amount    DECIMAL(18,2) DEFAULT 0,
    status          NVARCHAR(20) DEFAULT 'BORRADOR',
    created_at      DATETIME DEFAULT GETDATE()
);
GO

-- DETALLE DE COTIZACION
CREATE TABLE quote_items (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    quote_id        INT NOT NULL REFERENCES quotes(id),
    product_id      INT NOT NULL REFERENCES products(id),
    provider_id     INT NOT NULL REFERENCES providers(id),
    quantity        DECIMAL(18,2) NOT NULL,
    unit_price      DECIMAL(18,2) NOT NULL,
    tax_percent     DECIMAL(5,2) DEFAULT 19.0,
    subtotal        DECIMAL(18,2) NOT NULL
);
GO

-- DATOS DE PRUEBA
INSERT INTO categories (name, description) VALUES 
('Materiales', 'Materiales de construcción'),
('Herramientas', 'Herramientas y equipos'),
('Eléctricos', 'Materiales eléctricos'),
('Plomería', 'Materiales de plomería');
GO