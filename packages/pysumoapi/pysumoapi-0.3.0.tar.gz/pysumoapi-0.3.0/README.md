# PySumoAPI

[![PyPI version](https://badge.fury.io/py/pysumoapi.svg)](https://badge.fury.io/py/pysumoapi)
[![Python Versions](https://img.shields.io/pypi/pyversions/pysumoapi.svg)](https://pypi.org/project/pysumoapi/)
[![License](https://img.shields.io/github/license/colebrumley/pysumoapi.svg)](https://github.com/colebrumley/pysumoapi/blob/main/LICENSE)
[![Tests](https://github.com/colebrumley/pysumoapi/actions/workflows/test.yml/badge.svg)](https://github.com/colebrumley/pysumoapi/actions/workflows/test.yml)
[![Codecov](https://codecov.io/gh/colebrumley/pysumoapi/branch/main/graph/badge.svg)](https://codecov.io/gh/colebrumley/pysumoapi)

A Python client library for the [Sumo API](https://sumo-api.com), providing easy access to sumo wrestling data including rikishi information, statistics, shikona history, measurements, and rank history.

## Features

- Asynchronous API client using `httpx`
- Strongly typed data models using `pydantic`
- Comprehensive error handling

## Installation

```bash
# Using pip
pip install pysumoapi
```

## Quick Start

```python
import asyncio
from pysumoapi.client import SumoClient

async def main():
    async with SumoClient() as client:
        # Get rikishi information
        rikishi = await client.get_rikishi(1511)
        print(f"Name: {rikishi.shikona_en}")
        
        # Get rikishi statistics
        stats = await client.get_rikishi_stats(1511)
        print(f"Total matches: {stats.total_matches}")
        
        # Get shikona history
        shikonas = await client.get_shikonas(rikishi_id=1511, sort_order="asc")
        for shikona in shikonas:
            print(f"Basho: {shikona.basho_id}, Shikona: {shikona.shikona_en}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Synchronous Usage (SumoSyncClient)

For environments where asyncio is not ideal (e.g., scripts, Jupyter notebooks), `SumoSyncClient` provides a synchronous interface:

```python
from pysumoapi import SumoSyncClient

# All constructor arguments from SumoClient are also available for SumoSyncClient
with SumoSyncClient(base_url="https://sumo-api.com") as client:
    try:
        rikishi = client.get_rikishi(rikishi_id="1") # Example call
        print(rikishi.shikona_en)
    except Exception as e:
        print(f"An error occurred: {e}")
```
The `SumoSyncClient` wraps the asynchronous `SumoClient` and manages an event loop internally when its methods are called. It **must** be used as a context manager (with a `with` statement).

## API Reference

### SumoClient

The main client class for interacting with the Sumo API.

```python
from pysumoapi.client import SumoClient

# Initialize with custom base URL and SSL verification
async with SumoClient(base_url="https://sumo-api.com", verify_ssl=True) as client:
    # Use the client here
```

#### Methods

- `get_rikishi(rikishi_id: str) -> Rikishi`: Get information about a rikishi
  - Raises `ValueError` if rikishi_id is invalid

- `get_rikishi_stats(rikishi_id: str) -> RikishiStats`: Get statistics for a rikishi
  - Raises `ValueError` if rikishi_id is invalid

- `get_rikishis(shikona_en: Optional[str] = None, heya: Optional[str] = None, sumodb_id: Optional[int] = None, nsk_id: Optional[int] = None, intai: Optional[bool] = None, measurements: bool = True, ranks: bool = True, shikonas: bool = True, limit: int = 10, skip: int = 0) -> RikishiList`: Get a list of rikishi with optional filters
  - Raises `ValueError` if any ID parameters are invalid

- `get_rikishi_matches(rikishi_id: int, basho_id: Optional[str] = None) -> RikishiMatchesResponse`: Get all matches for a specific rikishi
  - Raises `ValueError` if:
    - rikishi_id is not positive
    - basho_id is not in YYYYMM format

- `get_rikishi_opponent_matches(rikishi_id: int, opponent_id: int, basho_id: Optional[str] = None) -> RikishiOpponentMatchesResponse`: Get all matches between two specific rikishi
  - Raises `ValueError` if:
    - rikishi_id or opponent_id is not positive
    - basho_id is not in YYYYMM format

- `get_basho(basho_id: str) -> Basho`: Get details for a specific basho tournament
  - Raises `ValueError` if:
    - basho_id is not in YYYYMM format
    - basho date is in the future

- `get_banzuke(basho_id: str, division: str) -> Banzuke`: Get banzuke details for a specific basho and division
  - Raises `ValueError` if:
    - basho_id is not in YYYYMM format
    - basho date is in the future
    - division is not one of: Makuuchi, Juryo, Makushita, Sandanme, Jonidan, Jonokuchi
  - Automatically converts match records to unified Match model

- `get_torikumi(basho_id: str, division: str, day: int) -> Torikumi`: Get torikumi details for a specific basho, division, and day
  - Raises `ValueError` if:
    - basho_id is not in YYYYMM format
    - basho date is in the future
    - division is not one of: Makuuchi, Juryo, Makushita, Sandanme, Jonidan, Jonokuchi
    - day is not between 1 and 15
  - Automatically converts matches to unified Match model

- `get_kimarite(sort_field: Optional[str] = None, sort_order: Optional[str] = "asc", limit: Optional[int] = None, skip: Optional[int] = 0) -> KimariteResponse`: Get statistics on kimarite usage
  - Raises `ValueError` if:
    - sort_field is not one of: count, kimarite, lastUsage
    - sort_order is not 'asc' or 'desc'
    - limit is not positive
    - skip is negative

- `get_kimarite_matches(kimarite: str, sort_order: Optional[str] = "asc", limit: Optional[int] = None, skip: Optional[int] = 0) -> KimariteMatchesResponse`: Get matches where a specific kimarite was used
  - Raises `ValueError` if:
    - kimarite is empty
    - sort_order is not 'asc' or 'desc'
    - limit is not positive or exceeds 1000
    - skip is negative

- `get_measurements(basho_id: Optional[str] = None, rikishi_id: Optional[int] = None, sort_order: Optional[str] = "desc") -> MeasurementsResponse`: Get measurement changes by rikishi or basho
  - Raises `ValueError` if:
    - Neither basho_id nor rikishi_id is provided
    - basho_id is not in YYYYMM format
    - rikishi_id is not positive
    - sort_order is not 'asc' or 'desc'
  - Automatically sorts results by basho_id if requested

- `get_ranks(basho_id: Optional[str] = None, rikishi_id: Optional[int] = None, sort_order: Optional[str] = "desc") -> RanksResponse`: Get rank changes by rikishi or basho
  - Raises `ValueError` if:
    - Neither basho_id nor rikishi_id is provided
    - basho_id is not in YYYYMM format
    - rikishi_id is not positive
    - sort_order is not 'asc' or 'desc'
  - Automatically sorts results by basho_id if requested

- `get_shikonas(basho_id: Optional[str] = None, rikishi_id: Optional[int] = None, sort_order: Optional[str] = "desc") -> ShikonasResponse`: Get shikona changes by rikishi or basho
  - Raises `ValueError` if:
    - Neither basho_id nor rikishi_id is provided
    - basho_id is not in YYYYMM format
    - rikishi_id is not positive
    - sort_order is not 'asc' or 'desc'
  - Automatically sorts results by basho_id if requested

### Data Models

- `Rikishi`: Information about a rikishi
- `RikishiList`: List of rikishi with pagination information
- `RikishiStats`: Statistics for a rikishi
- `RikishiMatchesResponse`: Response containing rikishi matches
- `RikishiOpponentMatchesResponse`: Response containing matches between two rikishi
- `Basho`: Information about a basho tournament
- `Banzuke`: Banzuke details for a division
- `RikishiBanzuke`: Individual rikishi entry in a banzuke
- `Torikumi`: Match schedule for a specific day
- `YushoWinner`: Information about a yusho winner
- `Match`: Unified model for sumo matches across all endpoints
- `KimariteResponse`: Statistics about kimarite usage
- `KimariteMatch`: Information about a match where a specific kimarite was used
- `KimariteMatchesResponse`: Response containing matches with a specific kimarite
- `Measurement`: Physical measurements of a rikishi
- `MeasurementsResponse`: Response containing measurement records
- `Rank`: Rank information for a rikishi
- `RanksResponse`: Response containing rank records
- `Shikona`: Shikona (ring name) information
- `ShikonasResponse`: Response containing shikona records
- `DivisionStats`: Statistics broken down by division
- `Sansho`: Special prize information
- `RikishiPrize`: Information about a rikishi who won a prize

## Examples

See the [examples](examples/) directory for more detailed examples:

- [Shikona Example](examples/shikona_example.py): Demonstrates retrieving and displaying shikona history
- [Comprehensive Example](examples/comprehensive_example.py): Shows how to use multiple endpoints together to create a comprehensive rikishi profile

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/colebrumley/pysumoapi.git
cd pysumoapi

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Using Make

This project includes a Makefile to automate common development tasks:

```bash
# Show available commands
make help

# Install the package in development mode
make setup

# Clean build artifacts and caches
make clean

# Run tests
make test

# Run linters
make lint

# Format code
make format

# Build the package
make build

# Publish to PyPI (requires PYPI_API_TOKEN environment variable)
make publish

# Show current version
make version

# Bump version (major, minor, or patch)
make version-bump TYPE=patch

# Set version explicitly
make version-set VERSION=1.0.0
```

### Version Management

The package includes a version management script (`scripts/version.py`) to help with versioning:

```bash
# Show current version
python scripts/version.py show

# Bump version (major, minor, or patch)
python scripts/version.py bump --type patch

# Set version explicitly
python scripts/version.py set --version 1.0.0
```

The script automatically:
- Updates version in `pyproject.toml`
- Updates `CHANGELOG.md` with a new version entry
- Validates version format
- Handles version bumping according to semantic versioning

### Release Process

To create a new release:

1. Ensure you're on the `main` branch and it's up to date:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Run the release script:
   ```bash
   # For a patch release (0.1.0 -> 0.1.1)
   make release TYPE=patch

   # For a minor release (0.1.0 -> 0.2.0)
   make release TYPE=minor

   # For a major release (0.1.0 -> 1.0.0)
   make release TYPE=major
   ```

   The release script (`scripts/release.py`) performs the following checks and steps:
   - Verifies git working directory is clean
   - Confirms you're on the main branch
   - Ensures local branch is up to date with remote
   - Checks for required dependencies
   - Verifies PyPI token is set (if publishing)
   - Bumps version using version.py
   - Runs tests
   - Runs linters
   - Builds the package
   - Publishes to PyPI (if PYPI_API_TOKEN is set)
   - Creates a git tag
   - Commits changes
   - Pushes to GitHub

   You can skip certain steps using flags:
   ```bash
   # Skip tests and linting
   make release TYPE=patch --skip-tests --skip-lint

   # Skip publishing to PyPI
   make release TYPE=patch --skip-publish

   # Skip creating a git tag
   make release TYPE=patch --skip-tag

   # Skip pre-release checks
   make release TYPE=patch --skip-checks
   ```

3. The script will prompt you to:
   - Review the changes
   - Confirm the release
   - Push the changes and tag

Note: The release process requires:
- Python 3.11 or later
- `uv` for dependency management
- `PYPI_API_TOKEN` environment variable for publishing to PyPI
- Git configured with proper credentials
