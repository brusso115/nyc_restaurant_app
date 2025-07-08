-- Restaurants
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT,
    url TEXT UNIQUE,
    address TEXT,
    city TEXT,
    region TEXT,
    postal_code TEXT,
    country TEXT,
    latitude FLOAT,
    longitude FLOAT,
    telephone TEXT,
    rating FLOAT,
    review_count INTEGER
);

-- Menu Items
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id),
    section TEXT,
    name TEXT,
    description TEXT,
    price FLOAT,
    currency TEXT,
    embedded BOOLEAN DEFAULT FALSE,
    UNIQUE (restaurant_id, name)
);

-- Store Links
CREATE TABLE store_links (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    address TEXT,
    status TEXT,
    last_scraped TIMESTAMP,
    updated_at TIMESTAMP,
    error TEXT
);

-- Categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

-- Restaurant ↔ Category mapping
CREATE TABLE restaurant_categories (
    restaurant_id INTEGER REFERENCES restaurants(id),
    category_id INTEGER REFERENCES categories(id),
    PRIMARY KEY (restaurant_id, category_id)
);

-- Restaurant Hours
CREATE TABLE restaurant_hours (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id),
    day TEXT,
    opens TIME,
    closes TIME,
    CONSTRAINT unique_hours UNIQUE (restaurant_id, day, opens, closes)
);
