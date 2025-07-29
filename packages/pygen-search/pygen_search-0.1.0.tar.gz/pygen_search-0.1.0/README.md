# PyGenSearch: Generic Python Search SDK

PyGenSearch is a lightweight, generic search SDK for Python applications. It allows you to easily implement in-memory search functionality for lists of dictionaries, focusing on specific fields.

## Features

- Simple to integrate and use.
- Search across multiple specified fields in your data.
- Basic text cleaning and tokenization.
- Configurable searchable fields.

## Installation

```bash
pip install pygen-search
```

## Usage

### Basic Python Example

```python
from pygen_search import PyGenSearch

data = [
    {"id": 1, "title": "Learn AI Today", "desc": "Machine Learning is fun.", "category": "tech"},
    {"id": 2, "title": "Python Tips", "desc": "Advanced tricks with Python.", "category": "programming"},
]

engine = PyGenSearch(data, searchable_fields=["title", "desc"])
results = engine.search("python")
print(results)
```

### Flask API Example

```python
from flask import Flask, request, jsonify
from pygen_search import PyGenSearch

app = Flask(__name__)

data = [
    {"id": 1, "title": "Learn AI Today", "desc": "Machine Learning is fun.", "category": "tech"},
    {"id": 2, "title": "Python Tips", "desc": "Advanced tricks with Python.", "category": "programming"},
]
engine = PyGenSearch(data, searchable_fields=["title", "desc"])

@app.route("/search")
def search():
    query = request.args.get("q", "")
    results = engine.search(query)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
```

### Integrate with HTML/JS Frontend

You can create a simple frontend that calls your Flask API:

**HTML/JS Example:**
```html
<input id="search" placeholder="Search...">
<ul id="results"></ul>
<script>
document.getElementById('search').addEventListener('input', async function() {
    const q = this.value;
    const res = await fetch('/search?q=' + encodeURIComponent(q));
    const data = await res.json();
    document.getElementById('results').innerHTML =
        data.map(item => `<li>${item.title}</li>`).join('');
});
</script>
```

### Integrate with React/Next.js

In your React or Next.js app, call your Flask API:

```jsx
// Example React component
import { useState } from "react";

function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  async function handleSearch(e) {
    setQuery(e.target.value);
    const res = await fetch(`/search?q=${encodeURIComponent(e.target.value)}`);
    const data = await res.json();
    setResults(data);
  }

  return (
    <div>
      <input value={query} onChange={handleSearch} placeholder="Search..." />
      <ul>
        {results.map(item => <li key={item.id}>{item.title}</li>)}
      </ul>
    </div>
  );
}

export default Search;
```

## License

MIT License. See [LICENSE](LICENSE) for details. 