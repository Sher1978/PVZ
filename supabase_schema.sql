-- Enable vector extension for CLIP image & text embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable trigram extension for fuzzy title search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(64),
    first_name VARCHAR(128) NOT NULL,
    language_code VARCHAR(8) DEFAULT 'ru',
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);

-- 2. Categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL
);

-- 3. Master Products table with pgvector column
CREATE TABLE IF NOT EXISTS master_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(512) NOT NULL,
    brand VARCHAR(128),
    category_id INT REFERENCES categories(id),
    main_image_url TEXT,
    description TEXT,
    embedding vector(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_master_products_brand ON master_products(brand);
CREATE INDEX IF NOT EXISTS idx_master_products_trgm ON master_products USING gin (title gin_trgm_ops);

-- HNSW Index for ultra-fast vector cosine similarity search in Supabase
CREATE INDEX IF NOT EXISTS idx_master_products_vector ON master_products USING hnsw (embedding vector_cosine_ops);

-- 4. Offers table
CREATE TABLE IF NOT EXISTS offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_id UUID REFERENCES master_products(id) ON DELETE CASCADE,
    platform VARCHAR(32) NOT NULL,
    external_sku VARCHAR(128) NOT NULL,
    title VARCHAR(512) NOT NULL,
    current_price NUMERIC(12, 2) NOT NULL,
    old_price NUMERIC(12, 2),
    currency VARCHAR(3) DEFAULT 'RUB',
    product_url TEXT NOT NULL,
    image_url TEXT,
    in_stock BOOLEAN DEFAULT TRUE,
    rating NUMERIC(3, 2),
    reviews_count INT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_platform_sku UNIQUE (platform, external_sku)
);

CREATE INDEX IF NOT EXISTS idx_offers_master_id ON offers(master_id);
CREATE INDEX IF NOT EXISTS idx_offers_price ON offers(current_price);

-- 5. Price History table
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    offer_id UUID NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
    price NUMERIC(12, 2) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_price_history_offer_time ON price_history(offer_id, recorded_at DESC);

-- 6. Price Alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    master_id UUID NOT NULL REFERENCES master_products(id) ON DELETE CASCADE,
    target_price NUMERIC(12, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    notify_on_any_drop BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_active ON price_alerts(master_id) WHERE is_active = TRUE;
