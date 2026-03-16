# Quickstart

## Goal

Get a list of Hacker News stories and open a story link from the terminal.

## Example Usage

```bash
# List top stories
hn list --feed top --limit 30

# View story details
hn story --id <story_id>

# View story comments
hn comments --id <story_id>

# Get story link
hn link --id <story_id>
```

## Expected Output (JSON)

Commands return JSON that includes story metadata, comment threads, or story
links depending on the command. See `contracts/commands.md` for schemas.
