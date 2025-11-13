-- ============================================================================
-- PostgreSQL Initialization Script for LolaAppJp
-- ============================================================================
-- This script runs automatically when the database container is first created
-- ============================================================================

-- Set timezone to Asia/Tokyo
SET timezone = 'Asia/Tokyo';

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create custom types (will be created by Alembic, but having them here doesn't hurt)
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('ADMIN', 'TORISHIMARIYAKU', 'KEIRI', 'TANTOSHA', 'HAKEN_SHAIN', 'UKEOI');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE candidate_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'HIRED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE employee_status AS ENUM ('ACTIVE', 'ON_LEAVE', 'RESIGNED', 'TERMINATED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE contract_type AS ENUM ('HAKEN', 'UKEOI', 'SEISHAIN');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE request_type AS ENUM ('NYUSHA', 'YUKYU', 'TAISHA', 'TRANSFER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE request_status AS ENUM ('DRAFT', 'PENDING', 'APPROVED', 'REJECTED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE yukyu_transaction_type AS ENUM ('GRANT', 'USE', 'EXPIRE', 'ADJUSTMENT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE '✅ LolaAppJp database initialized successfully';
    RAISE NOTICE '   Timezone: %', current_setting('timezone');
    RAISE NOTICE '   Extensions created: uuid-ossp, pg_trgm';
    RAISE NOTICE '   Custom types created: 7 ENUM types';
END $$;
