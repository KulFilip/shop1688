import os
import psycopg2
from psycopg2.extras import RealDictCursor

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    offer_id VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) DEFAULT 'power bank',
    title_pl VARCHAR(500) NOT NULL,
    title_ua VARCHAR(500) NOT NULL,
    description_pl TEXT,
    description_ua TEXT,
    weight VARCHAR(100),
    dimensions VARCHAR(100),
    main_image TEXT,
    images JSONB DEFAULT '[]'::jsonb,
    price_cny NUMERIC(10, 2),
    margin NUMERIC(5, 2) DEFAULT 0.30,
    price_pln NUMERIC(10, 2),
    price_uah NUMERIC(10, 2),
    min_order_quantity INT DEFAULT 1,
    in_stock BOOLEAN DEFAULT true,
    -- Internal / Manager confidential fields (not shown to customers)
    source_platform VARCHAR(50) DEFAULT '1688',
    source_url TEXT,
    source_seller VARCHAR(255),
    raw_attributes JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_offer_id ON products(offer_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
"""

def get_connection(connection_uri: str = None):
    uri = connection_uri or os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_9OjchouZIza3@ep-lucky-firefly-ba72e19j.c-8.eu-central-1.aws.neon.tech/neondb?sslmode=require"
    if not uri:
        raise ValueError("DATABASE_URL must be set")
    return psycopg2.connect(uri)

def init_db(connection_uri: str = None):
    with get_connection(connection_uri) as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()

