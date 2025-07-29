# pygen_search/config.py

def normalize_data(raw_data, fields=None):
    """
    Convert any supported data (list of dicts, DB results, etc.)
    into a standard format: list of dicts with selected fields only.
    """
    if fields is None:
        return raw_data

    normalized = []
    for item in raw_data:
        norm_item = {field: item.get(field, "") for field in fields}
        normalized.append(norm_item)
    return normalized
