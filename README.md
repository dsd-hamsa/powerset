# PowerSet Package

A comprehensive Python package for PowerTrack solar monitoring platform automation.

## Installation

```bash
pip install powerset
# or for development
pip install -e .
```

## Quick Start

```python
from powerset.api import APIClient
from powerset.auth import load_env, update_auth_from_fetch

# Refresh authentication from mostRecentFetch.js
update_auth_from_fetch()

# Load auth and create API client
auth = load_env()
client = APIClient(auth)

# Fetch site hardware data
hardware = client.make_request('/api/view/sitehardwareproduction/S60308')
print(hardware)
```

## Features

- **Unified Authentication**: Automatic refresh from Chrome DevTools fetch files
- **Intelligent API Client**: Built-in retries, error handling, and rate limiting
- **Organized Logging**: Script-specific logs with timestamps and structured output
- **Database Integration**: SQLite-based data persistence with transaction safety
- **Data Processing**: Utilities for extracting and transforming PowerTrack data

## Scripts

Example scripts demonstrating package usage are available in the `scripts/` directory:

- `fetch_site_data.py`: Comprehensive site data extraction (hardware, alerts, modeling)

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black powerset/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request