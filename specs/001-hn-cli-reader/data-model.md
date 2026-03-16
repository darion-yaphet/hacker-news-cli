# Data Model

## Story

**Fields**
- id (identifier)
- title (non-empty)
- author (non-empty)
- score (non-negative integer)
- age (timestamp or relative age)
- url (valid URL)
- comment_count (non-negative integer)
- feed (reference to Feed)

**Relationships**
- Story has many Comments
- Story belongs to a Feed

**Validation Rules**
- id must be present and unique within a list
- title and author must be non-empty
- score and comment_count must be >= 0
- url must be present and valid

## Comment

**Fields**
- id (identifier)
- author (may be missing for deleted comments)
- timestamp (may be missing if deleted)
- content (may be empty or missing for deleted comments)
- parent_id (Story or Comment reference)

**Relationships**
- Comment belongs to a Story
- Comment may reference a parent Comment

**Validation Rules**
- id must be present
- parent_id must reference a Story or Comment

## Feed

**Fields**
- name (top, new, best, ask, show, jobs)
- display_label

**Relationships**
- Feed contains many Stories

**Validation Rules**
- name must be one of the supported feed identifiers

## State Transitions (if applicable)

- Stories and comments may transition to "deleted" or "unavailable" states and
  should remain displayable with placeholders.
