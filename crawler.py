import requests
import bs4
from collections import deque
import re
import csv
import unicodedata
from urllib.parse import urljoin, urlparse, unquote
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys

START_URL = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
DOMAIN = "educacionvirtual.javeriana.edu.co"

STOP_WORDS = {
    'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no',
    'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del',
    'las', 'una', 'curso', 'cursos', 'programa', 'programas',
    'estudiante', 'estudiantes', 'profesional', 'profesionales',
    'universidad', 'educacion', 'virtual', 'javeriana', 'formacion',
    'aprendizaje', 'conocimiento', 'habilidades', 'competencias',
    'area', 'nivel', 'duracion', 'horas', 'precio', 'fecha', 'inicio',
    'inscripcion', 'certificado', 'pontificia', 'continua'
}

METADATA_KEYWORDS = {
    'duracion', 'hora', 'horas', 'precio', 'nivel', 'fecha', 'inicio',
    'inscripcion', 'certificado', 'profesor', 'profesora', 'docente',
    'instructor', 'instructora', 'tutor', 'tutora', 'modalidad',
    'cupos', 'cupo', 'intensidad', 'horario'
}

WORD_RE = re.compile(r"[a-záéíóúüñ0-9_]+", re.IGNORECASE)


def normalize_word(word: str) -> str:
    """Return normalized word: lowercase, no diacritics, trimmed."""
    if not word:
        return ''
    word = word.lower()
    nfkd = unicodedata.normalize("NFKD", word)
    word = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return word.strip()


def is_metadata_text(text: str) -> bool:
    """Return True if text likely contains course metadata."""
    if not text:
        return False
    norm = normalize_word(text)
    for kw in METADATA_KEYWORDS:
        if kw in norm:
            return True
    return False


def extract_words(text: str):
    """Yield normalized words from text, excluding stopwords."""
    if not text:
        return
    for match in WORD_RE.finditer(text):
        w = match.group()
        if len(w) <= 1:
            continue
        norm = normalize_word(w)
        if not norm or norm in STOP_WORDS:
            continue
        yield norm


def setup_driver():
    """Return headless Chrome driver for Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception:
        return None


def get_course_id_from_url(url: str) -> str:
    """Extract course slug from URL, decoding percent-encoding."""
    try:
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split('/') if p]
        if not parts:
            return None
        last = parts[-1]
        last = unquote(last)
        last = normalize_word(last)
        last = last.replace(' ', '-')
        last = re.sub(r'[^a-z0-9\-_]', '', last)
        return last or None
    except Exception:
        return None


def _bs4_from_element(element):
    """Return BeautifulSoup object from Selenium element or bs4 tag."""
    if hasattr(element, "get_attribute"):
        inner = element.get_attribute("innerHTML") or ''
        return bs4.BeautifulSoup(inner, "html5lib")
    return bs4.BeautifulSoup(str(element), "html5lib")


def clean_title(title: str) -> str:
    """Remove generic suffix from course titles."""
    if not title:
        return title
    suffix = (" - Educación Continua de la Pontificia Universidad "
              "Javeriana - Portal Universitario")
    return title.replace(suffix, "").strip()


def extract_course_from_element(element, base_url=None):
    """Return (id, title, description, url) from a course element."""
    try:
        curso_url = None
        if hasattr(element, "get_attribute"):
            try:
                a = element.find_element(By.TAG_NAME, "a")
                curso_url = a.get_attribute("href")
            except Exception:
                curso_url = None
        else:
            a = element.find("a")
            if a and a.has_attr("href"):
                curso_url = a["href"]

        if not curso_url:
            return None

        if base_url:
            curso_url = urljoin(base_url, curso_url)
        if DOMAIN not in urlparse(curso_url).netloc:
            return None

        curso_id = get_course_id_from_url(curso_url)
        if not curso_id:
            return None

        soup = _bs4_from_element(element)

        title_sel = [
            "b.card-title", ".card-title", "h3", "h4", "h5", "a > b", "a"
        ]
        titulo = None
        for sel in title_sel:
            t = soup.select_one(sel)
            if t and t.get_text(strip=True):
                titulo = t.get_text(strip=True)
                break
        if not titulo:
            text_nodes = [
                s.strip() for s in soup.get_text(separator="\n").splitlines()
                if s.strip()
            ]
            titulo = text_nodes[0] if text_nodes else "Sin título"
        titulo = clean_title(titulo)

        description_parts = []
        desc_selectors = [
            "div[class*='descripcion']",
            "div.description",
            "p.card-text",
            "p"
        ]
        for sel in desc_selectors:
            for p in soup.select(sel):
                txt = p.get_text(" ", strip=True)
                if not txt or is_metadata_text(txt):
                    continue
                words = txt.split()
                if len(words) < 4 and any(char.isdigit() for char in txt):
                    continue
                if len(txt) >= 30 or sel != "p":
                    description_parts.append(txt)

        if not description_parts:
            all_text = soup.get_text(" ", strip=True)
            for sentence in re.split(r'[.!?]\s+', all_text):
                if not is_metadata_text(sentence) and len(sentence) >= 50:
                    description_parts.append(sentence)
            if not description_parts:
                lines = [
                    l.strip() for l in all_text.splitlines()
                    if l.strip() and not is_metadata_text(l)
                ]
                if lines:
                    lines = sorted(lines, key=lambda s: -len(s))
                    description_parts = lines[:3]

        descripcion = " ".join(description_parts).strip() if description_parts else ""
        return curso_id, titulo, descripcion, curso_url
    except Exception:
        return None


def extract_all_courses_from_catalog(driver):
    """Extract courses using Selenium (handles dynamic content)."""
    courses_data = {}
    try:
        driver.get(START_URL)
        time.sleep(4)
        course_selectors = [
            "div.card-body",
            "div.item-programa",
            "div[class*='card']",
            "article",
        ]
        for sel in course_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                if not elements:
                    continue
                for el in elements:
                    info = extract_course_from_element(el, base_url=START_URL)
                    if info:
                        cid, title, desc, url = info
                        if cid not in courses_data:
                            courses_data[cid] = {
                                'titulo': title,
                                'descripcion': desc,
                                'url': url
                            }
            except Exception:
                continue
        return courses_data
    except Exception:
        return courses_data


def load_more_courses_with_scroll(driver, max_scrolls=20):
    """Return more courses by scrolling and clicking 'load more'."""
    additional_courses = {}
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)
            buttons = driver.find_elements(
                By.CSS_SELECTOR,
                ("button[class*='load'], button[class*='more'], "
                 "a[class*='load'], button[class*='mas']")
            )
            for btn in buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                except Exception:
                    continue
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1
        elems = driver.find_elements(
            By.CSS_SELECTOR, "div.card-body, div.item-programa, article"
        )
        for el in elems:
            info = extract_course_from_element(el, base_url=START_URL)
            if info:
                cid, title, desc, url = info
                if cid not in additional_courses:
                    additional_courses[cid] = {
                        'titulo': title,
                        'descripcion': desc,
                        'url': url
                    }
    except Exception:
        return additional_courses
    return additional_courses


def visit_course_page(url):
    """Return (id, title, description, url) from a course page."""
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code != 200:
            return None
        soup = bs4.BeautifulSoup(resp.text, "html5lib")
        curso_id = get_course_id_from_url(url)
        meta = soup.select_one("meta[name='description']")
        meta_og = soup.select_one("meta[property='og:description']")
        descripcion = ""
        if meta and meta.get('content'):
            descripcion = meta.get('content').strip()
        elif meta_og and meta_og.get('content'):
            descripcion = meta_og.get('content').strip()
        else:
            for sel in [
                "div[class*='descripcion']", "div.description",
                "div[class*='content']", "article"
            ]:
                elems = soup.select(sel)
                if elems:
                    texts = [
                        e.get_text(" ", strip=True)
                        for e in elems if not is_metadata_text(e.get_text())
                    ]
                    if texts:
                        descripcion = max(texts, key=len)
                        break
            if not descripcion:
                paras = [
                    p.get_text(" ", strip=True) for p in soup.find_all("p")
                ]
                paras = [
                    p for p in paras if p and not is_metadata_text(p) and len(p) > 40
                ]
                if paras:
                    descripcion = " ".join(paras[:3])
                else:
                    descripcion = soup.get_text(" ", strip=True)[:1000]
        title_elem = soup.select_one("h1, .title, .card-title, title")
        titulo = (
            title_elem.get_text(strip=True)
            if title_elem
            else (descripcion.split(".")[0] if descripcion else "Sin título")
        )
        titulo = clean_title(titulo)
        return curso_id, titulo, descripcion, url
    except Exception:
        return None


def go(n: int, dictionary: str, output: str):
    """Main crawler. Returns (index, courses_data)."""
    driver = setup_driver()
    index = {}
    courses_data = {}
    if driver:
        try:
            courses_data = extract_all_courses_from_catalog(driver)
        finally:
            try:
                driver.quit()
            except Exception:
                pass
    if courses_data:
        enriched = {}
        limit = min(50, len(courses_data))
        count = 0
        for cid, info in list(courses_data.items()):
            if count >= limit:
                break
            res = visit_course_page(info['url'])
            if res:
                _, titulo, descripcion, url = res
                enriched[cid] = {
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'url': info['url']
                }
            else:
                enriched[cid] = info
            count += 1
        for cid, info in courses_data.items():
            if cid not in enriched:
                enriched[cid] = info
        courses_data = enriched
    for cid, info in courses_data.items():
        full_text = " ".join([info.get('titulo', ''), info.get('descripcion', '')])
        for w in extract_words(full_text):
            index.setdefault(w, set()).add(cid)
    save_results(index, courses_data, output)
    return index, courses_data


def save_results(index, courses_data, output):
    """Save index in CSV and courses in JSON."""
    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        for word in sorted(index.keys()):
            for cid in sorted(index[word]):
                writer.writerow([cid, word])
    course_info_file = output.replace('.csv', '_courses.json')
    with open(course_info_file, "w", encoding="utf-8") as f:
        json.dump(courses_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        index, courses = go(1000, "diccionario.json", "indice.csv")
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        import traceback
        traceback.print_exc()
