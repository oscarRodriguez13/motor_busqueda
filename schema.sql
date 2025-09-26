DROP TABLE IF EXISTS indice;

CREATE TABLE indice (
    id SERIAL PRIMARY KEY,
    curso_id VARCHAR(255),
    palabra VARCHAR(255)
);

-- Cargar desde CSV
