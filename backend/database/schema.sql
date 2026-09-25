-- ============================================
-- VikriMitra Database Schema
-- PostgreSQL 16
-- ============================================


-- ============================================
-- 1. CUSTOMERS
-- ============================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INTEGER NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state CHAR(2) NOT NULL
);


-- ============================================
-- 2. SELLERS
-- ============================================

CREATE TABLE IF NOT EXISTS sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INTEGER NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state CHAR(2) NOT NULL
);


-- ============================================
-- 3. PRODUCTS
-- ============================================

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),

    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,

    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC
);


-- ============================================
-- 4. CATEGORY TRANSLATION
-- ============================================

CREATE TABLE IF NOT EXISTS category_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100) NOT NULL
);


-- ============================================
-- 5. ORDERS
-- ============================================

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,

    order_status VARCHAR(30) NOT NULL,

    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,

    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- ============================================
-- 6. ORDER ITEMS
-- ============================================

CREATE TABLE IF NOT EXISTS order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INTEGER NOT NULL,

    product_id VARCHAR(50),
    seller_id VARCHAR(50),

    shipping_limit_date TIMESTAMP,

    price NUMERIC(12, 2) NOT NULL,
    freight_value NUMERIC(12, 2) NOT NULL,

    PRIMARY KEY (order_id, order_item_id),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_order_items_seller
        FOREIGN KEY (seller_id)
        REFERENCES sellers(seller_id)
);


-- ============================================
-- 7. ORDER PAYMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS order_payments (
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INTEGER NOT NULL,

    payment_type VARCHAR(30) NOT NULL,
    payment_installments INTEGER NOT NULL,
    payment_value NUMERIC(12, 2) NOT NULL,

    PRIMARY KEY (order_id, payment_sequential),

    CONSTRAINT fk_order_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- ============================================
-- 8. ORDER REVIEWS
-- ============================================

CREATE TABLE IF NOT EXISTS order_reviews (
    review_pk BIGSERIAL PRIMARY KEY,

    review_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,

    review_score INTEGER NOT NULL,

    review_comment_title TEXT,
    review_comment_message TEXT,

    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,

    CONSTRAINT fk_order_reviews_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- ============================================
-- 9. GEOLOCATION
-- ============================================

CREATE TABLE IF NOT EXISTS geolocation (
    geolocation_id BIGSERIAL PRIMARY KEY,

    geolocation_zip_code_prefix INTEGER NOT NULL,

    geolocation_lat NUMERIC,
    geolocation_lng NUMERIC,

    geolocation_city VARCHAR(100),
    geolocation_state CHAR(2)
);


-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
    ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp
    ON orders(order_purchase_timestamp);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
    ON order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_order_items_seller_id
    ON order_items(seller_id);

CREATE INDEX IF NOT EXISTS idx_order_payments_order_id
    ON order_payments(order_id);

CREATE INDEX IF NOT EXISTS idx_order_reviews_order_id
    ON order_reviews(order_id);

CREATE INDEX IF NOT EXISTS idx_geolocation_zip_code
    ON geolocation(geolocation_zip_code_prefix);

-- ============================================
-- 10. DASHBOARD CHARTS
-- ============================================

CREATE TABLE IF NOT EXISTS dashboard_charts (
    id BIGSERIAL PRIMARY KEY,

    query TEXT NOT NULL,

    chart_type VARCHAR(50) NOT NULL,

    chart_config JSONB NOT NULL,

    insight TEXT,

    data_snapshot JSONB,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);