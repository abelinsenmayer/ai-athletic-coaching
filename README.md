# AI Athletic Coaching

AI Athletic Coaching Project

## Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management.

### Installation

1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Development

- Run tests: `poetry run pytest`
- Format code: `poetry run black .`
- Lint code: `poetry run flake8`
- Type checking: `poetry run mypy .`

## Project Structure

```
.
├── pyproject.toml    # Poetry configuration and dependencies
├── .gitignore        # Git ignore file
├── README.md         # This file
└── src/              # Source code (to be created)
```
