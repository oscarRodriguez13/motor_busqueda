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


def search(keywords: list[str], courses: dict, top_k: int = 10) -> list[tuple[str, str, float]]:
    """
    Searches for the most relevant courses given a list of keywords.
    
    Args:
        keywords: List of interest words.
        courses: Dictionary with course_id -> {titulo, descripcion, url}.
        top_k: Number of top results to return.
    
    Returns:
        List of tuples (course_id, url, score) sorted by score (descending).
    """
    query = " ".join(keywords)
    results = []

    for course_id, info in courses.items():
        text = f"{info.get('titulo', '')} {info.get('descripcion', '')}"
        score = cosine_similarity(query, text)
        if score > 0:
            results.append((course_id, info.get("url", ""), score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    with open("indice_courses.json", "r", encoding="utf-8") as file:
        courses = json.load(file)

    # Example query
    interests = ["fotografía", "arte"]

    found = search(interests, courses, top_k=5)

    for cid, url, score in found:
        print(f"{cid} | {url} | Relevance: {score:.3f}")
