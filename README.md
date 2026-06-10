# Hacker News CLI

A terminal-first command-line tool for browsing Hacker News. Read stories, view comments, and access links without leaving your terminal.

## Features

- **Browse story lists** — View top, new, best, ask, show, and job stories
- **View story details** — See full story metadata including title, author, score, and comment count
- **Read threaded comments** — Comment trees rendered with indentation, HTML converted to text, with depth and count limits
- **Get story links** — Quickly extract URLs for opening in your browser
- **Login / logout / whoami** — Authenticate against news.ycombinator.com with a locally persisted session
- **Interactive mode** — A REPL that reuses one HTTP session across commands
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

Commands: `list`, `story`, `comments`, `link`, `login`, `logout`, `whoami`, `interactive`, and `help`.

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

Display the comment thread for a story. Replies are indented under their
parent; `depth` in the JSON output records the nesting level:

```bash
hn comments --id 39528747 --format text

# Limit how deep the thread is fetched (1 = top-level comments only)
hn comments --id 39528747 --depth 2

# Cap the total number of comments fetched (parents are kept before replies)
hn comments --id 39528747 --max-comments 50
```

Without `--depth` / `--max-comments` the entire thread is fetched.

### Get story link

Extract the URL for a story:

```bash
hn link --id 39528747
```

### Login, logout, whoami

Sessions are persisted to `~/.config/hn-cli/auth.json` (override with the
`HN_CLI_AUTH_FILE` environment variable):

```bash
# Interactive login: prompts for username and password
hn login

# Scripted login: password comes from the environment, never from CLI args
HN_CLI_PASSWORD=... hn login --username alice

# Check the current session (no network request when no session is saved)
hn whoami

# Log out remotely and clear the local session
hn logout
```

There is intentionally no `--password` flag — a password on the command line
would leak into shell history and `ps` output.

### Interactive mode

```bash
hn interactive
```

Starts a `>` prompt that accepts the same commands (with or without the `hn`
prefix) and reuses one HTTP connection across them. Exit with `exit`/`quit`.

### Output formats

All data commands support `--format`. `list` defaults to `text`; `story`,
`comments`, and `link` default to `json`:

```bash
# Structured data for scripting
hn list --format json

# Formatted tables and readable text
hn story --id 39528747 --format text
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
├── auth.py     # Persisted login session (cookies + username)
├── models.py   # Data models (Story, Comment)
├── output.py   # JSON output formatting
└── render.py   # Text rendering with Rich library
```

### API Client

The `HNClient` class wraps the [Hacker News Firebase API](https://github.com/HackerNews/API)
and the news.ycombinator.com web interface (for login state) with:
- Automatic retries with exponential backoff on all requests
- Configurable timeouts
- Connection pooling via `requests.Session`
- Concurrent story and comment fetching
- Failed items are skipped with a warning instead of failing the whole page

### Data Models

Immutable dataclasses for core entities:
- **Story** — title, author, score, age, URL, comment count
- **Comment** — author, age, content (HTML converted to text), thread depth

## Development

### Setup

```bash
# Install dependencies, including the dev group
uv sync
```

### Running tests

```bash
uv run pytest

# With the coverage gate (fails under 80%)
uv run pytest --cov=hn_cli
```

### Code quality

```bash
# Linting
uv run ruff check .

# Type checking
uv run mypy src/hn_cli

# Formatting
uv run ruff format .
```

## License

[Your License Here]
