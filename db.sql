-- Drop existing database if needed and create a new one
DROP DATABASE IF EXISTS ecommerce;
CREATE DATABASE ecommerce;
USE ecommerce;

-- Users table with primary key and necessary fields
CREATE TABLE users (
    id INT AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    address TEXT,
    phone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email)
) ENGINE=InnoDB;


-- Sellers table with foreign key reference to users
CREATE TABLE sellers (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    shop_name VARCHAR(100) NOT NULL,
    shop_description TEXT,
    logo_url VARCHAR(255),
    banner_url VARCHAR(255),
    theme_color VARCHAR(7) DEFAULT '#ffffff',
    is_verified BOOLEAN DEFAULT FALSE,
    commission_rate DECIMAL(5,2) DEFAULT 5.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Categories table with self-referencing relationship for hierarchical categories
CREATE TABLE categories (
    id INT AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    parent_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Products table with foreign keys to sellers and categories
CREATE TABLE products (
    id INT AUTO_INCREMENT,
    seller_id INT NOT NULL,
    category_id INT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    discount_price DECIMAL(10,2),
    stock_quantity INT DEFAULT 0,
    barcode VARCHAR(50),
    sku VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX (name),
    INDEX (price)
) ENGINE=InnoDB;

-- Product images table
CREATE TABLE product_images (
    id INT AUTO_INCREMENT,
    product_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Reviews table with check constraint for rating
CREATE TABLE reviews (
    id INT AUTO_INCREMENT,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address TEXT NOT NULL,
    order_status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Order items table with foreign key references
CREATE TABLE order_items (
    id INT AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Shopping cart table with unique constraint on user_id and product_id
CREATE TABLE cart (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY (user_id, product_id)
) ENGINE=InnoDB;

-- Pages table for seller stores
CREATE TABLE pages (
    id INT AUTO_INCREMENT,
    seller_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    slug VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE,
    UNIQUE KEY (seller_id, slug)
) ENGINE=InnoDB;

-- Insert sample admin user
INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin)
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:150000$abc123', 'Admin', 'User', TRUE);

-- Insert sample categories
INSERT INTO categories (name, description)
VALUES 
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Home & Garden', 'Items for home and garden');

INSERT INTO categories (name, description) VALUES
('Beauty & Personal Care', 'Skincare, makeup, haircare and grooming products'),
('Health & Wellness', 'Vitamins, supplements and fitness equipment'),
('Books & Media', 'Books, ebooks, movies and music'),
('Toys & Games', 'Toys, board games and recreational products'),
('Pet Supplies', 'Food, accessories and care products for pets'),
('Office & Stationery', 'Office supplies, desk accessories and stationery'),
('Automotive', 'Car parts, accessories and tools'),
('Food & Beverages', 'Gourmet food, snacks, coffee and drinks');


-- Create stored procedure for getting product details
DELIMITER //
CREATE PROCEDURE get_product_details(IN product_id_param INT)
BEGIN
    SELECT p.*, c.name AS category_name, s.shop_name, 
           AVG(r.rating) AS average_rating, COUNT(r.id) AS review_count
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.id
    LEFT JOIN sellers s ON p.seller_id = s.id
    LEFT JOIN reviews r ON p.id = r.product_id
    WHERE p.id = product_id_param
    GROUP BY p.id;
END //
DELIMITER ;

-- Create function to check if product is in stock
DELIMITER //
CREATE FUNCTION is_product_in_stock(product_id_param INT) 
RETURNS BOOLEAN DETERMINISTIC
BEGIN
    DECLARE stock INT;
    SELECT stock_quantity INTO stock FROM products WHERE id = product_id_param;
    RETURN stock > 0;
END //
DELIMITER ;

-- Create index for product search
CREATE INDEX product_search_idx ON products(name, description(100));

-- Create view for product listings
CREATE VIEW product_listings AS
SELECT 
    p.id, p.name, p.price, p.discount_price, 
    p.stock_quantity, p.is_active,
    c.name AS category_name,
    s.shop_name,
    AVG(r.rating) AS avg_rating,
    COUNT(DISTINCT r.id) AS review_count,
    pi.image_url AS primary_image
FROM 
    products p
LEFT JOIN 
    categories c ON p.category_id = c.id
LEFT JOIN 
    sellers s ON p.seller_id = s.id
LEFT JOIN 
    reviews r ON p.id = r.product_id
LEFT JOIN 
    product_images pi ON p.id = pi.product_id AND pi.is_primary = TRUE
WHERE 
    p.is_active = TRUE
GROUP BY 
    p.id;
