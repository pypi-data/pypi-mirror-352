# Vector Store Client

A Python client for interacting with Vector Store API services. This client provides a convenient interface for working with vector embeddings, semantic search, and metadata filtering.

[![PyPI Version](https://img.shields.io/pypi/v/vector-store-client.svg)](https://pypi.org/project/vector-store-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/vector-store-client.svg)](https://pypi.org/project/vector-store-client/)
[![License](https://img.shields.io/pypi/l/vector-store-client.svg)](https://pypi.org/project/vector-store-client/)

## Features

- Full-featured API for Vector Store operations
- Asynchronous interface based on `httpx`
- Automatic parameter handling and validation
- Comprehensive error management
- Support for all vector store operations:
  - Creating records from text or vectors
  - Vector similarity search
  - Metadata filtering
  - Record management

## Installation

```bash
pip install vector-store-client
```

Or install from source:

```bash
git clone https://github.com/yourusername/vector-store-client.git
cd vector-store-client
pip install -e .
```

## Quick Start

```python
import asyncio
from vector_store_client import create_client

async def main():
    # Create client with connection to the service
    client = await create_client(base_url="http://localhost:8007")
    
    # Create a record from text
    record_id = await client.create_text_record(
        text="Example text for vectorization",
        metadata={"type": "example", "tags": ["test", "vector"]}
    )
    
    # Search for similar records
    results = await client.search_text_records(
        text="vectorization example",
        limit=5
    )
    
    for result in results:
        print(f"ID: {result.id}, Similarity: {result.score:.4f}")
    
    # Close the client session
    await client._client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

Detailed documentation is available in both English and Russian:

- [English Documentation](docs/README.md)
- [Русская документация](docs/README.ru.md)

## Examples

Check out the example scripts to get started:

- [Basic Usage](examples/basic_usage.py) - Essential operations
- [Advanced Usage](examples/advanced_usage.py) - Complex scenarios and filtering

## Development

### Requirements

- Python 3.7+
- httpx
- pydantic

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
python run_tests.py
```

## License

MIT

# Пример использования

```python
# ...
record = await client.create_record(vector=vector, metadata=metadata)
print("Record ID:", record["record_id"])

text_record = await client.create_text_record(text="Some text", metadata=metadata)
print("Text Record ID:", text_record["record_id"])
# ... existing code ...
```
