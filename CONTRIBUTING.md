# Contributing

## Development Setup

1. Clone the repository
2. Install Python 3.12+
3. Create a virtual environment: `python -m venv .venv`
4. Activate it: `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Linux)
5. Install dependencies: `pip install -e ".[dev]"`

## Code Style

- Format with Black (line length 100)
- Lint with Ruff
- Type check with mypy

## Commit Messages

Use Conventional Commits: `feat:`, `fix:`, `docs:`, `ci:`, etc.
