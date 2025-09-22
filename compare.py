import json
import math
from collections import Counter
from crawler import extract_words


def cosine_similarity(text_one: str, text_two: str) -> float:
    """
    Computes cosine similarity between two texts.
    Returns a value in the range [0, 1].
    """
    words_one = list(extract_words(text_one))
    words_two = list(extract_words(text_two))
    if not words_one or not words_two:
        return 0.0

    vector_one = Counter(words_one)
    vector_two = Counter(words_two)

    common_terms = set(vector_one.keys()) & set(vector_two.keys())
    dot_product = sum(vector_one[w] * vector_two[w] for w in common_terms)

    norm_one = math.sqrt(sum(v ** 2 for v in vector_one.values()))
    norm_two = math.sqrt(sum(v ** 2 for v in vector_two.values()))

    if norm_one == 0 or norm_two == 0:
        return 0.0
    return dot_product / (norm_one * norm_two)


def compare(course_one: dict, course_two: dict) -> float:
    """
    Compares two courses using title and description.
    Returns a value in the range [0, 1].
    """
    text_one = f"{course_one.get('titulo', '')} {course_one.get('descripcion', '')}"
    text_two = f"{course_two.get('titulo', '')} {course_two.get('descripcion', '')}"
    return cosine_similarity(text_one, text_two)


if __name__ == "__main__":
    with open("indice_courses.json", "r", encoding="utf-8") as file:
        courses = json.load(file)

    course_id_one = "vulnerabilidad-desastres-y-cambio-climatico-en-latinoamerica"
    course_id_two = "huella-de-carbono-en-el-sector-constructor"

    course_one = courses[course_id_one]
    course_two = courses[course_id_two]

    print("Curso 1:", course_one["titulo"])
    print("Curso 2:", course_two["titulo"])
    print("Cosine similarity:", compare(course_one, course_two))
