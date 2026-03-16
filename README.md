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

### Running the Evaluation Test Suite

To run the video clip evaluation test suite:

```bash
python -m tests.test_runner <root_directory>
```

Where `<root_directory>` is the path to a directory containing:
- `clips/` - Directory with video files (any format)
- `evals/` - Directory with evaluation files

Each video file in `clips/` should have a corresponding evaluation file in `evals/` named `<video_name>-eval.txt`. The evaluation files should contain JSON objects with the following structure:
```json
{
  "score": 85.5,
  "feedbackText": "Good form, slight improvement needed in follow-through"
}
```

#### Example Directory Structure
```
test_data/
├── clips/
│   ├── clip1.mp4
│   ├── clip2.avi
│   └── clip3.mov
└── evals/
    ├── clip1-eval.txt
    ├── clip2-eval.txt
    └── clip3-eval.txt
```

