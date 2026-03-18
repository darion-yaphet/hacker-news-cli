# Hacker News CLI

A terminal-first command-line tool for browsing Hacker News. Read stories, view comments, and access links without leaving your terminal.

## Features

- **Browse story lists** — View top, new, best, ask, show, and job stories
- **View story details** — See full story metadata including title, author, score, and comment count
- **Read comments** — Display comment threads in a readable format with HTML-to-text conversion
- **Get story links** — Quickly extract URLs for opening in your browser
- **Multiple output formats** — JSON for scripting, text for human readability
- **Resilient API client** — Automatic retries with exponential backoff for network failures

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd hacker-news-cli

# Install with uv
uv pip install -e .

# Or install with pip
pip install -e .
```

## Usage

The CLI provides four main commands: `list`, `story`, `comments`, and `link`.

### List stories

Display a feed of stories (default: top stories):

```bash
# List top stories (default)
hn list

# List a specific feed
hn list --feed new
hn list --feed best
hn list --feed ask
hn list --feed show
hn list --feed jobs

# Paginate results
hn list --limit 10 --page 2
```

### View story details

Show detailed information for a specific story:

```bash
hn story --id 39528747
```

### Read comments

Display the comment thread for a story:

```bash
hn comments --id 39528747
```

### Get story link

Extract the URL for a story:

```bash
hn link --id 39528747
```

### Output formats

All commands support `--format` option:

```bash
# JSON output (default) - structured data for scripting
hn list --format json

# Text output - formatted tables and readable text
hn list --format text
```

### Connection options

Configure API client behavior:

```bash
hn list --timeout 15 --retries 3 --backoff 1.0
```

## Examples

```bash
# Get the top 5 stories in text format
hn list --limit 5 --format text

# View comments for the top story
TOP_STORY=$(hn list --limit 1 --format json | jq -r '.items[0].id')
hn comments --id "$TOP_STORY" --format text

# Open a story URL in the default browser
hn link --id 39528747 | xargs open
```

## Architecture

The project follows a layered architecture:

```
src/hn_cli/
├── cli.py      # Command-line interface and argument parsing
├── client.py   # Hacker News API client with retry logic
├── models.py   # Data models (Story, Comment, Feed)
├── output.py   # JSON output formatting
└── render.py   # Text rendering with Rich library
```

### API Client

The `HNClient` class wraps the [Hacker News Firebase API](https://github.com/HackerNews/API) with:
- Automatic retries with exponential backoff
- Configurable timeouts
- Connection pooling via `requests.Session`

### Data Models

Immutable dataclasses for core entities:
- **Story** — title, author, score, age, URL, comment count
- **Comment** — author, age, content (HTML converted to text)
- **Feed** — named story collections (top, new, best, etc.)

## Development

### Setup

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Code quality

```bash
# Linting
ruff check .

# Type checking
mypy src/hn_cli

# Formatting
ruff format .
```

## License

[Your License Here]
