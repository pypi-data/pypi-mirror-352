# pygen_search/core.py

from pygen_search.utils import tokenize
from pygen_search.config import normalize_data

class PyGenSearch:
    def __init__(self, data, searchable_fields=None):
        """
        data: list of dicts
        searchable_fields: list of keys to include in search
        """
        self.searchable_fields = searchable_fields or []
        self.data = normalize_data(data, self.searchable_fields)

    def search(self, query: str, limit=10):
        """
        Basic keyword match search. Case-insensitive, token-based.
        """
        if not query.strip():
            return []

        query_tokens = set(tokenize(query))
        results = []

        for record in self.data:
            combined = " ".join(str(record.get(field, "")) for field in self.searchable_fields)
            text_tokens = set(tokenize(combined))

            if query_tokens & text_tokens:
                results.append(record)

            if len(results) >= limit:
                break

        return results
