# json2markdown

A Python library to convert JSON data to Markdown documents.

## Installation

```bash
pip install json2markdown
```

## Usage

```python
import json2markdown

json_data = {
    "name": "Example",
    "description": "A simple example",
    "items": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]
}

markdown_output = json2markdown.convert_json_to_markdown_document(json_data)
print(markdown_output)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.