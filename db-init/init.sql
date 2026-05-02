-- Extensión para generar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========
-- ENUMS
-- ========

CREATE TYPE deployment_type AS ENUM ('dockerfile', 'docker-compose');

CREATE TYPE project_status AS ENUM ('building', 'running', 'stopped', 'idle');


-- =============
-- TABLA: users
-- =============

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ===============
-- TABLA: projects
-- ===============

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    nombre TEXT NOT NULL,
    repo_url TEXT NOT NULL,

    deployment_type deployment_type NOT NULL,

    puerto_externo INTEGER NOT NULL,

    containers_ids TEXT[], -- IDs de los contenedores del proyecto en Docker

    repo_path TEXT, -- Ruta local del repositorio clonado

    estado project_status NOT NULL DEFAULT 'building',

    ultimo_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    user_id UUID NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ========
-- ÍNDICES
-- ========

CREATE INDEX idx_projects_user_id ON projects(user_id);

CREATE INDEX idx_projects_estado ON projects(estado);

CREATE INDEX idx_projects_ultimo_acceso ON projects(ultimo_acceso);