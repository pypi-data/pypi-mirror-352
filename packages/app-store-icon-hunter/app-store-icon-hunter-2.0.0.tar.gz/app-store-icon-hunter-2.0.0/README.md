# 🚀 App Store Icon Hunter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#testing)

**A powerful command-line tool and REST API for searching apps and downloading their icons from App Store and Google Play Store in multiple sizes.**

Perfect for developers, designers, and anyone who needs quick access to high-quality app icons for mockups, presentations, or development projects.

## ✨ Features

### 🎯 Dual Interface

- **Interactive CLI** with user-friendly menus and selection
- **REST API Server** for programmatic access and integration
- **Cross-platform** support (Windows, macOS, Linux)

### 🔍 Comprehensive Search

- **App Store** search using iTunes Search API
- **Google Play Store** search via SerpApi integration
- **Multi-store** search capabilities
- **Country-specific** search results

### 📱 Icon Management

- **Multiple sizes**: 16px to 1024px icons
- **Batch downloads** with progress tracking
- **Custom size selection**
- **Organized file structure** with app-specific folders

### 🎨 User Experience

- **Interactive selection** - choose specific apps to download
- **Bulk download** option for all search results
- **Real-time progress** indicators
- **Detailed app information** display with ratings and prices

## 🏗️ Project Structure

```
app-store-icon-hunter/
├── README.md
├── setup.py
├── requirements.txt
├── .gitignore
├── LICENSE
├── app_store_icon_hunter/          # Main package
│   ├── __init__.py
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py                 # Enhanced CLI with interactive selection
│   ├── api/                        # REST API server
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI server
│   ├── core/                       # Core functionality
│   │   ├── __init__.py
│   │   ├── app_store.py           # App Store API integration
│   │   ├── google_play.py         # Google Play API integration
│   │   └── downloader.py          # Icon downloading logic
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       └── helpers.py             # Helper functions
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_api.py
│   └── test_core.py
├── docs/                           # Documentation
│   ├── api.md                     # API documentation
│   ├── cli.md                     # CLI documentation
│   └── examples.md                # Usage examples
└── examples/                       # Example scripts
    ├── basic_usage.py             # Basic usage example
    ├── api-example.py             # API client example
    └── batch_download.py          # Batch download example
```

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install app-store-icon-hunter

# Or install from source
git clone https://github.com/Garyku0/app-store-icon-hunter.git
cd app-store-icon-hunter
pip install -e .
```

### Environment Setup

For Google Play Store search functionality, you'll need a SerpApi key:

```bash
export SERPAPI_KEY="your_serpapi_key_here"
```

### Basic CLI Usage

```bash
# Search and select apps interactively
icon-hunter search "Instagram"

# Search specific store
icon-hunter search "WhatsApp" --store appstore

# Auto-download all results
icon-hunter search "Spotify" --auto-download

# Custom icon sizes and output directory
icon-hunter search "Telegram" --sizes "64,128,256" --output "./my_icons"

# Interactive mode with guided prompts
icon-hunter interactive
```

# Custom icon sizes

icon-hunter search "Discord" --sizes 64,128,256,512

# Download specific app

icon-hunter download "Twitter" --sizes 128,256

````

### API Server Usage

```bash
# Start the API server
icon-hunter server
# or
uvicorn app_store_icon_hunter.api.main:app --reload --port 8000

# Server will be available at:
# http://localhost:8000 - API endpoints
# http://localhost:8000/docs - Interactive documentation
````

## 📖 Detailed Usage

### CLI Commands

#### Search Command

The enhanced search command now provides interactive selection:

```bash
icon-hunter search [SEARCH_TERM] [OPTIONS]
```

**Options:**

- `--store`: Choose store (`appstore`, `googleplay`, `both`)
- `--country`: Country code (default: `us`)
- `--limit`: Maximum results (default: `10`)
- `--output`: Output directory (default: `icons`)
- `--sizes`: Comma-separated icon sizes
- `--auto-download/--interactive`: Download mode

**Interactive Mode Example:**

```bash
$ icon-hunter search "Instagram"
🔍 Searching for 'Instagram' in both...

================================================================================
#   App Name                           Store           Price      Rating
================================================================================
1   Instagram                          App Store       Free       4.5/5
2   Instagram Lite                     Google Play     Free       4.2/5
3   Instagram for Business             App Store       Free       4.1/5
================================================================================

Options:
• Enter numbers separated by commas (e.g., 1,3,5)
• Enter 'all' to download all apps
• Enter 'q' to quit

Your choice: 1,2

📥 Downloading icons in sizes: 64, 128, 256, 512...
✓ Downloaded 4 icon sizes for Instagram
✓ Downloaded 4 icon sizes for Instagram Lite

✅ Successfully downloaded icons for 2 apps
📁 Icons saved to: /path/to/icons
```

#### Download Command

Direct download for specific apps:

```bash
icon-hunter download [APP_NAME] [OPTIONS]
```

#### Server Command

Start the API server:

```bash
icon-hunter server
```

#### Config Command

View current configuration:

```bash
icon-hunter config
```

### REST API Endpoints

#### Search Apps

```http
POST /search
```

**Request Body:**

```json
{
  "term": "Instagram",
  "store": "both",
  "country": "us",
  "limit": 10
}
```

**Response:**

```json
[
  {
    "name": "Instagram",
    "bundle_id": "com.burbn.instagram",
    "icon_url": "https://is1-ssl.mzstatic.com/image/thumb/Purple123/v4/...",
    "store": "App Store",
    "price": "Free",
    "rating": 4.5,
    "description": "Instagram is a simple way to capture and share..."
  }
]
```

#### Download Icons

```http
POST /download
```

**Request Body:**

```json
{
  "apps": [
    {
      "name": "Instagram",
      "icon_url": "https://...",
      "bundle_id": "com.burbn.instagram"
    }
  ],
  "sizes": [64, 128, 256, 512],
  "format": "zip"
}
```

**Response:**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "message": "Download job started for 1 apps",
  "status_url": "/status/123e4567-e89b-12d3-a456-426614174000"
}
```

#### Check Download Status

```http
GET /status/{job_id}
```

**Response:**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": 1,
  "total": 1,
  "download_url": "/download/123e4567-e89b-12d3-a456-426614174000"
}
```

#### Download Files

```http
GET /download/{job_id}
```

Returns the ZIP file with all downloaded icons.

## 🔧 Configuration

### Environment Variables

```bash
# Google Play Store API (optional)
export SERPAPI_KEY="your_serpapi_key_here"

# Custom output directory
export ICON_HUNTER_OUTPUT_DIR="/path/to/downloads"

# API server configuration
export ICON_HUNTER_HOST="0.0.0.0"
export ICON_HUNTER_PORT="8000"
```

### Supported Icon Sizes

The tool supports all standard icon sizes:

- **Tiny**: 16px, 32px
- **Small**: 48px, 64px
- **Medium**: 128px, 256px
- **Large**: 512px, 1024px

**Platform-specific recommendations:**

- **iOS**: 57, 72, 114, 144, 512, 1024
- **Android**: 48, 72, 96, 144, 192
- **Web**: 16, 32, 48, 96, 128
- **Desktop**: 128, 256, 512

## 🧪 Examples

### Python API Client

```python
import requests

# Search for apps
response = requests.post("http://localhost:8000/search", json={
    "term": "Instagram",
    "store": "appstore",
    "limit": 5
})
apps = response.json()

# Start download
download_response = requests.post("http://localhost:8000/download", json={
    "apps": apps[:2],  # Download first 2 apps
    "sizes": [128, 256, 512],
    "format": "zip"
})
job_id = download_response.json()["job_id"]

# Check status
status_response = requests.get(f"http://localhost:8000/status/{job_id}")
print(status_response.json())
```

### Batch Processing Script

```python
#!/usr/bin/env python3
import subprocess
import time

apps_to_download = [
    "Instagram", "WhatsApp", "Twitter", "Facebook", "Snapchat"
]

for app in apps_to_download:
    print(f"Downloading {app}...")
    subprocess.run([
        "icon-hunter", "download", app,
        "--sizes", "128,256,512",
        "--output", f"icons/{app.lower()}"
    ])
    time.sleep(1)  # Be respectful to APIs

print("All downloads completed!")
```

## 🏃‍♂️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/username/app-store-icon-hunter.git
cd app-store-icon-hunter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app_store_icon_hunter

# Run specific test file
pytest tests/test_cli.py
```

### Code Quality

```bash
# Format code
black app_store_icon_hunter/

# Lint code
flake8 app_store_icon_hunter/

# Type checking
mypy app_store_icon_hunter/
```

### Building and Publishing

```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI (with proper credentials)
twine upload dist/*
```

## 📝 API Documentation

When running the API server, interactive documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/your-username/app-store-icon-hunter.git
cd app-store-icon-hunter
pip install -e ".[dev]"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **iTunes Search API** for App Store data
- **SerpApi** for Google Play Store integration
- **Click** for the beautiful CLI interface
- **FastAPI** for the high-performance API server
- **Contributors** who make this project better

## 🐛 Bug Reports & Feature Requests

Please use [GitHub Issues](https://github.com/Garyku0/app-store-icon-hunter/issues) to report bugs or request features.

**Bug Report Template:**

```
**Description**
A clear description of the bug.

**Steps to Reproduce**
1. Run command '...'
2. See error

**Expected Behavior**
What should happen.

**Environment**
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.9.0]
- Version: [e.g., 2.0.0]
```

## 📈 Roadmap

### Version 2.1.0

- [ ] Image resizing with PIL/Pillow
- [ ] SVG icon support
- [ ] Batch processing from CSV files
- [ ] Desktop GUI application

### Version 2.2.0

- [ ] Icon optimization and compression
- [ ] Advanced filtering options
- [ ] Custom icon processing pipelines
- [ ] Integration with design tools (Figma, Sketch)

### Version 3.0.0

- [ ] Machine learning-based icon similarity search
- [ ] Icon generation and customization
- [ ] Cloud storage integration
- [ ] Team collaboration features

## 📊 Performance

### Benchmarks

- **Search Performance**: ~500ms per API call
- **Download Speed**: ~2MB/s average (network dependent)
- **Concurrent Downloads**: Up to 10 simultaneous
- **Memory Usage**: <50MB typical

### Optimization Tips

1. Use smaller icon size sets for faster downloads
2. Leverage the `--auto-download` flag for batch operations
3. Set up API keys for Google Play Store access
4. Use the API server for high-frequency operations

## 🔐 Security

### API Security

- CORS enabled for web integration
- Rate limiting on endpoints
- Input validation and sanitization
- Secure file handling

### Privacy

- No user data collection
- No icon content modification
- Temporary file cleanup
- Respect for API rate limits

---

**Made with ❤️ for the developer community**

_If this project helped you, please consider giving it a ⭐ on GitHub!_
