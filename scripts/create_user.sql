CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    username varchar(100) NOT NULL UNIQUE,
    email varchar(200) UNIQUE,
    hashed_password varchar(255) NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);

WITH input_data AS (
    SELECT
        'admin'::text AS username,
        'admin123'::text AS password,
        'admin@example.com'::text AS email,
        true::boolean AS is_active
)
INSERT INTO users (id, username, email, hashed_password, is_active)
SELECT
    uuid_generate_v4(),
    input_data.username,
    NULLIF(input_data.email, ''),
    crypt(input_data.password, gen_salt('bf')),
    input_data.is_active
FROM input_data
ON CONFLICT (username) DO UPDATE
SET hashed_password = crypt(
        (SELECT password FROM input_data),
        gen_salt('bf')
    ),
    email = NULLIF((SELECT email FROM input_data), ''),
    is_active = (SELECT is_active FROM input_data),
    updated_at = now();
