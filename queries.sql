-- Buscar todos los cursos que contienen una palabra dada
SELECT curso_id
FROM indice
WHERE palabra = 'fotografia';

-- Contar frecuencia de palabras en un curso
SELECT palabra, COUNT(*) AS frecuencia
FROM indice
WHERE curso_id = 'propiedad-horizontal'
GROUP BY palabra
ORDER BY frecuencia DESC;
