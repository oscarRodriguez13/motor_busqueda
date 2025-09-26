# Laboratorio 2 – Motor de Búsqueda de Cursos

## Objetivo
Este proyecto implementa un motor de búsqueda sencillo sobre el catálogo de cursos de la Pontificia Universidad Javeriana.  
Se desarrolla un sistema completo compuesto por un **crawler** para la recolección de datos, un **indexador** para organizar la información, un **buscador** para recuperar cursos relevantes según intereses y un **comparador de similitud** que permite analizar la relación entre cursos existentes.

## Componentes del proyecto
- **crawler.py** – Rastrea el catálogo oficial de cursos, extrae título, descripción y URL, y construye un índice palabra → curso.
- **schema.sql** – Script SQL para crear la tabla en PostgreSQL y cargar el índice generado.
- **queries.sql** – Consultas SQL para localizar cursos que contengan una palabra específica o realizar búsquedas por texto.
- **search.py** – Implementa la función `search(keywords)` que retorna una lista de cursos ordenados por relevancia según las palabras clave ingresadas.
- **compare.py** – Implementa la función `compare(curso1, curso2)` que calcula la similitud entre dos cursos en el rango [0, 1].
- **slides.pdf** – Presentación en formato PDF utilizada como soporte para la sustentación del laboratorio.

## Tecnologías utilizadas
- **Lenguaje:** Python 3.10+
- **Base de datos:** PostgreSQL 14+
- **Librerías:**  
  - `requests` – Para realizar peticiones HTTP.  
  - `beautifulsoup4` y `html5lib` – Para el análisis y extracción de contenido HTML.  
  - `selenium` – Para la interacción con contenido dinámico.  
  - `psycopg2` – Para la conexión con PostgreSQL.  

## Ejecución
1. Crear el entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   pip install -r requirements.txt
