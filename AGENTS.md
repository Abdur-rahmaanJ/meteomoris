# AGENTS.md

## Project Overview

**meteomoris** is a Python package that scrapes weather data from the Mauritius Meteorological Services website (`http://metservice.intnet.mu`) and exposes it as a Python API and CLI tool. Current version: `2.13.0`.

## Project Structure

```
meteomoris/
├── meteomoris/           # Main package
│   ├── __init__.py       # Public API exports and version
│   ├── __main__.py       # CLI entry point (Click-based)
│   └── meteo.py          # Core Meteo class with all scraping/data methods
├── tests/
│   └── test_main.py      # Integration tests (require internet)
├── setup.py              # Package setup and publishing
├── setup.cfg
├── .github/workflows/    # CI: auto-publish to PyPI on release
└── debian/               # Debian packaging
```

## Tech Stack

- **Python 3.4+**
- **Dependencies**: `requests`, `beautifulsoup4`, `click`, `rich`
- **CLI framework**: Click (`meteomoris/__main__.py`)
- **Terminal rendering**: Rich (tables, panels, grids)
- **Web scraping**: BeautifulSoup4 + requests
- **Testing**: pytest

## Build & Install

```bash
# Create and activate virtual environment
python3.9 -m venv venv
. venv/bin/activate

# Install in editable mode
pip install -e .
```

## Testing

```bash
pip install pytest
python -m pytest tests/
```

Tests in `tests/test_main.py` are **integration tests** that require internet access — they call the live scraping functions and assert on return types.

## Architecture

- **`Meteo` class** (`meteomoris/meteo.py`): A class-based singleton pattern using `@classmethod` for all methods. All public API methods are classmethods on `Meteo`.
- **Public API** (`meteomoris/__init__.py`): Exposes `Meteo` classmethods as module-level functions (e.g., `get_weekforecast`, `get_moonphase`, `get_tides`, etc.).
- **CLI** (`meteomoris/__main__.py`): Click commands that call the public API with `print=True` for rich terminal output.
- **Caching**: Daily JSON file cache (`meteomoris_cache.json`) keyed by date. Cache is per-day — stale data is cleared automatically.
- **Internet check**: Optional connectivity check before fetching data (`Meteo.CHECK_INTERNET`, `Meteo.EXIT_ON_NO_INTERNET`).

## Code Conventions

- All data-fetching methods follow the pattern: check cache → fetch from web if missing → parse HTML → cache result → return data.
- Methods accept `print=True` (or `print_=True`) for rich terminal output via `rich.Table` / `rich.Panel`, otherwise return raw Python dicts/lists.
- Error handling is minimal — bare `except` clauses are common. Match existing style when editing.
- No type annotations used.
- No linter or formatter configured.

## Key Public API Methods

| Method | Returns |
|---|---|
| `get_weekforecast(day=None)` | `list[dict]` or `dict` |
| `get_cityforecast(day=None)` | `list[dict]` or `dict` |
| `get_moonphase(month=None)` | `dict` |
| `get_main_message(links=False)` | `str` or `list[tuple]` |
| `get_special_weather_bulletin()` | `str` |
| `get_eclipses()` | `list[dict]` |
| `get_equinoxes()` | `list[dict]` |
| `get_solstices()` | `list[dict]` |
| `get_tides()` | `dict` |
| `get_latest()` | `dict` |
| `get_uvindex()` | `dict` |
| `get_sunrisemu()` / `get_sunriserodr()` | `dict` |
| `get_moonrisemu()` / `get_moonriserodr()` | `dict` |
| `get_today_forecast()` | `dict` |
| `get_today_sunrise(country)` | `dict` |
| `get_today_eclipse()` | `dict` |
| `get_today_moonphase()` | `dict` |
| `get_today_tides()` | `list` |
| `get_today_solstice()` | `dict` |
| `get_today_equinox()` | `dict` |

## CLI Commands

`meteomoris forecast`, `meteomoris today [--rodr]`, `meteomoris message [--links]`, `meteomoris moonphase`, `meteomoris special`, `meteomoris sunrisemu`, `meteomoris sunriserodr`, `meteomoris moonrisemu`, `meteomoris moonriserodr`, `meteomoris uvindex`, `meteomoris version`

## Data Sources

- Primary: `http://metservice.intnet.mu` (Mauritius Meteorological Services)
- UV Index: `https://en.tutiempo.net/ultraviolet-index/{region}.html`

## Git Commits

Use conventional commit style based on the project's existing history:

- `feat: <description>` — new features or enhancements
- `fix: <description>` — bug fixes
- Descriptive messages using present tense (e.g., "Add moonrise functionality", not "Added moonrise")
- Keep the first line concise; add body details if needed

Examples from history:
- `feat: Add moonrise/moonset functionality for Mauritius and Rodrigues`
- `fix: Fix typo: Contition -> Condition`
- `fix: Fix sunrise info`
- `feat: Improve temperature readability`

## Publishing

- PyPI: auto-published via GitHub Actions on release (`python-publish.yml`)
- Manual: `python setup.py publish` (installs, builds, uploads via twine)
- Ubuntu PPA: via `debuild` and `dput`
