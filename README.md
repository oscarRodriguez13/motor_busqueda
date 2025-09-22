# Laboratorio 2 – Motor de búsqueda de cursos

## Objetivo
Este laboratorio implementa un motor de búsqueda simple para los cursos de la Universidad Javeriana.  
Se desarrolla un **crawler**, un **indexador**, un **buscador de cursos** y un **comparador de similitud** entre cursos.

## Componentes
- **crawler.py** → Rastrea el catálogo de cursos y construye un índice palabra → curso.
- **schema.sql** → Script para crear la tabla en PostgreSQL y cargar el índice.
- **queries.sql** → Consultas SQL para localizar cursos que contienen una palabra.
- **search.py** → Función `search(keywords)` que devuelve las URLs más relevantes.
- **compare.py** → Función `compare(curso1, curso2)` que devuelve similitud [0,1].
- **slides.pdf** → Presentación de soporte.

## Tecnologías
- Python 3.10+
- PostgreSQL 14+
- Librerías: `requests`, `beautifulsoup4`, `html5lib`, `psycopg2`

## Conclusiones
*(Aquí escribes lo que observes: eficiencia, limitaciones del crawler, utilidad de las métricas de similitud, etc.)*
