# CLI Contracts

## Command: List Stories

**Purpose**: Return a ranked list of stories from a selected feed.

**Inputs**
- feed: top | new | best | ask | show | jobs (default: top)
- limit: number of stories to return (default: 30)
- page: pagination offset (default: 1)

**Output (JSON)**
```json
{
  "feed": "top",
  "page": 1,
  "items": [
    {
      "id": "string",
      "title": "string",
      "author": "string",
      "score": 0,
      "age": "string",
      "comment_count": 0,
      "url": "string"
    }
  ]
}
```

## Command: Story Details

**Purpose**: Return story metadata for a given story identifier.

**Inputs**
- story_id: required identifier from the story list

**Output (JSON)**
```json
{
  "id": "string",
  "title": "string",
  "author": "string",
  "score": 0,
  "age": "string",
  "url": "string",
  "comment_count": 0
}
```

## Command: Story Comments

**Purpose**: Return a readable comment thread for a given story.

**Inputs**
- story_id: required identifier from the story list

**Output (JSON)**
```json
{
  "story_id": "string",
  "comments": [
    {
      "id": "string",
      "author": "string",
      "age": "string",
      "content": "string",
      "parent_id": "string"
    }
  ]
}
```

## Command: Story Link

**Purpose**: Return the URL for a given story identifier.

**Inputs**
- story_id: required identifier from the story list

**Output (JSON)**
```json
{
  "id": "string",
  "url": "string"
}
```
