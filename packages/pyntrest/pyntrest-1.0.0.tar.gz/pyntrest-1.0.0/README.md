# Pyntrest

A powerful Pinterest image search and download client with CLI and API support.

## Features

- Search and download Pinterest images
- Command-line interface
- FastAPI server with web interface
- Multiple search modes:
  - Regular search
  - Random images
  - Inspiration images
  - Single image quick search
- Download functionality
- Session management with cookie refresh
- User agent rotation to prevent rate limiting
- Easy to use as a Python library

## Installation

```bash
# From PyPI (coming soon)
pip install pyntrest

# From GitHub
git clone https://github.com/redmoon0x/pynterest.git
cd pynterest
pip install -e .
```

## Command Line Usage

Search and download images:
```bash
# Basic search
pyntrest-search "cats" -n 5

# Download to specific directory
pyntrest-search "dogs" -n 3 -o dog_pics

# Get random images
pyntrest-search random "nature" -n 2

# Get random inspiration images
pyntrest-search inspire -n 3
```

## Web Interface

Start the web server:
```bash
pyntrest-server
```

Then open http://localhost:8000 in your browser to use the web interface.

## API Usage

### As a Python Library

```python
from pyntrest import PinterestClient

# Initialize the client
client = PinterestClient()

# Search for images
images = client.get_image_links("cats", num_images=3)
for img in images:
    print(f"URL: {img['url']}")
    print(f"Size: {img['width']}x{img['height']}")
    print(f"Title: {img['title']}")
    print(f"Description: {img['description']}")

# Get a single image quickly
image = client.get_one_image("dogs")
print(image['url'])

# Get a random inspiration image
image = client.get_random_inspiration()
print(image['url'])
```

### REST API Endpoints

The web server provides these endpoints:

- `GET /api/search/?query=<term>&num=<count>` - Search for images
- `GET /api/random/?query=<term>` - Get a random image for query
- `GET /api/one/?query=<term>` - Get a single image quickly
- `GET /api/inspire/` - Get a random inspiration image
- `GET /api/download/?url=<image_url>` - Download an image

Example using curl:
```bash
# Search for images
curl "http://localhost:8000/api/search/?query=cats&num=3"

# Get a random image
curl "http://localhost:8000/api/random/?query=dogs"

# Get an inspiration
curl "http://localhost:8000/api/inspire/"
```

## Project Structure

```
pyntrest/
├── client/           # Core Pinterest client
│   ├── __init__.py
│   └── pinterest.py
├── api/             # FastAPI server
│   ├── __init__.py
│   └── server.py
├── web/            # Web interface
│   └── static/     # Frontend files
├── __init__.py     # Package initialization
└── cli.py         # Command line interface
```

## Development

1. Clone the repository
2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest
```

## License

MIT License - see LICENSE file for details.
