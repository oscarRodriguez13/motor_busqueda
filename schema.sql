DROP TABLE IF EXISTS indice;

CREATE TABLE indice (
    id SERIAL PRIMARY KEY,
    curso_id VARCHAR(255),
    palabra VARCHAR(255)
);

-- Cargar desde CSV (ajusta la ruta a tu máquina)
-- COPY requiere que el archivo esté accesible para PostgreSQL
-- Ejemplo en Linux/Mac:
-- COPY indice(curso_id, palabra) FROM '/ruta/indice.csv' DELIMITER '|' CSV;

-- En Windows puedes usar \copy desde psql:
-- \copy indice(curso_id, palabra) FROM 'C:/ruta/indice.csv' DELIMITER '|' CSV;
