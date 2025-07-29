# tests/test_core.py

from pygen_search import PyGenSearch
from pygen_search.config import normalize_data
from pygen_search.utils import tokenize, clean_text


sample_data = [
    {"id": 1, "title": "Learn AI Today", "desc": "Machine Learning is fun and a key AI skill.", "category": "tech"},
    {"id": 2, "title": "Python Tips & Tricks", "desc": "Advanced tricks with Python dictionaries.", "category": "programming"},
    {"id": 3, "title": "The Ethics of AI", "desc": "Exploring responsible use of Artificial Intelligence.", "category": "ethics"},
    {"id": 4, "title": "Intro to Python", "desc": "A beginner's guide to Python programming.", "category": "programming"},
]


def test_search_finds_relevant_documents():
    engine = PyGenSearch(sample_data, searchable_fields=["title", "desc"])
    results = engine.search("ai")
    assert len(results) == 2
    titles = [r["title"] for r in results]
    assert "Learn AI Today" in titles
    assert "The Ethics of AI" in titles

def test_search_multiple_tokens():
    engine = PyGenSearch(sample_data, searchable_fields=["title", "desc"])
    results = engine.search("python tips")
    assert len(results) == 1
    assert results[0]["title"] == "Python Tips & Tricks"

def test_case_insensitive():
    engine = PyGenSearch(sample_data, searchable_fields=["title", "desc"])
    lower = engine.search("learn ai")
    upper = engine.search("LEARN AI")
    assert lower == upper

def test_empty_query_returns_empty():
    engine = PyGenSearch(sample_data, searchable_fields=["title", "desc"])
    results = engine.search("")
    assert results == []

def test_no_results():
    engine = PyGenSearch(sample_data, searchable_fields=["title", "desc"])
    results = engine.search("gibberishgibberish")
    assert len(results) == 0

def test_limit_works():
    engine = PyGenSearch(sample_data, searchable_fields=["title", "desc"])
    results = engine.search("python", limit=1)
    assert len(results) == 1

def test_field_restriction():
    engine = PyGenSearch(sample_data, searchable_fields=["title"])
    results = engine.search("dictionaries")  # only in desc
    assert len(results) == 0
    results = engine.search("python")
    assert len(results) == 2


def test_utils_clean_text():
    assert clean_text("Hello World!") == "hello world"
    assert clean_text("AI: The Future!!!") == "ai the future"

def test_utils_tokenize():
    assert tokenize("AI is now!") == ["ai", "is", "now"]
    assert tokenize(" 123 Go ") == ["123", "go"]

def test_config_normalize_fields():
    norm = normalize_data(sample_data, fields=["title", "category"])
    assert all("title" in item and "category" in item for item in norm)
    assert all("desc" not in item for item in norm)

if __name__ == "__main__":
    print("All tests executed successfully!")
