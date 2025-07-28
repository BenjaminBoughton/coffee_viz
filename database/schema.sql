-- Coffee Shop Database Schema
-- Supports Hawaii POC with future US expansion

CREATE TABLE IF NOT EXISTS coffee_shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'HI',
    zip_code TEXT NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    signature_drink TEXT,
    rating REAL DEFAULT 0.0,
    description TEXT,
    phone TEXT,
    hours TEXT,
    website TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_zip_code ON coffee_shops(zip_code);
CREATE INDEX IF NOT EXISTS idx_city ON coffee_shops(city);
CREATE INDEX IF NOT EXISTS idx_state ON coffee_shops(state);
CREATE INDEX IF NOT EXISTS idx_rating ON coffee_shops(rating);
CREATE INDEX IF NOT EXISTS idx_location ON coffee_shops(lat, lng);

-- Reviews table for future expansion
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coffee_shop_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coffee_shop_id) REFERENCES coffee_shops(id)
);

-- Photos table for future expansion
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coffee_shop_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    caption TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coffee_shop_id) REFERENCES coffee_shops(id)
);

-- Tags table for categorization
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Coffee shop tags junction table
CREATE TABLE IF NOT EXISTS coffee_shop_tags (
    coffee_shop_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (coffee_shop_id, tag_id),
    FOREIGN KEY (coffee_shop_id) REFERENCES coffee_shops(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
); 