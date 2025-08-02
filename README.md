# anifiller

A simple CLI tool to identify and organize anime episodes by type (canon, mixed, filler) using data from [animefillerlist.com](https://www.animefillerlist.com).

## Features

- Get filler list of a particular show
- Get all shows available on [animefillerlist.com](https://www.animefillerlist.com)
- Smart suggestions
- Move filler/mixed episodes to a separate folder

## Installation

```bash
# PyPI package coming soon™
uv tool install git+https://github.com/JoshPaulie/anifiller.git
```

## Usage

Anifiller requires show names to be in "slug" format (lowercase, hyphenated) as they appear in animefillerlist.com URLs. If you're unsure of the correct slug, use [smart suggestions](#smart-suggestions) or [`--shows`](#filter-shows-by-name) to find it.

### Get episode information for a show

```bash
anifiller list dragon-ball
```

Output:
```
Canon: 1-28, 34-41, 43, 46-78, 84-126, 133-148
Mixed: 29, 42, 44
Filler: 30-33, 45, 79-83, 127-132, 149-153
```

### JSON output

```bash
anifiller list naruto --json
```

Output:

```jsonc
{
  "show_name": "dragon-ball",
  "manga_canon": [
    1,
    2,
    3,
    // ... truncated
  ],
  "mixed_canon_filler": [
    29,
    42,
    44
  ],
  "filler": [
    30,
    31,
    32,
    // ... truncated
  ],
  "summary": {
    "canon_count": 129,
    "mixed_count": 3,
    "filler_count": 21,
    "total_count": 153
  }
}
```

### List all available shows

```bash
anifiller list --shows
```

#### Filter shows by name

```bash
anifiller list --shows "dragon ball"
```

Output:
```jsonc
[
  // Some items were truncated
  {
    "name": "Dragon Ball",
    "slug": "dragon-ball"
  },
  {
    "name": "Dragon Ball GT",
    "slug": "dragon-ball-gt"
  },
  {
    "name": "Dragon Ball Super",
    "slug": "dragon-ball-super"
  },
  {
    "name": "Dragon Ball Z",
    "slug": "dragon-ball-z"
  },
  {
    "name": "Dragon Ball Z Kai",
    "slug": "dragon-ball-z-kai"
  },
]

```

### Smart suggestions

If you use the wrong show name, anifiller will suggest similar shows:

```bash
anifiller "dragon ball"
```

Output:
```
Error: Show not found

Did you mean one of these shows?
  Dragon Ball (slug: dragon-ball)
  Dragon Ball Z (slug: dragon-ball-z)
  Dragon Ball GT (slug: dragon-ball-gt)

Try: anifiller list dragon-ball
```

### Move filler episodes

Move filler and/or mixed episodes to a "filler" subfolder:

```bash
anifiller mover --directory /path/to/anime/episodes --slug naruto --filler
```

```bash
anifiller mover -d /path/to/episodes -s dragon-ball --filler --mixed
```

Supports various file naming patterns:
- `1. First Episode.mkv`
- `Episode 01.mp4`
- `S01E01.avi`
- `Ep01.mkv`

## Commands

- `list` - Show episode information and available shows
- `mover` - Move filler/mixed episodes to a separate folder

## Options

### List command
- `--json` - Output data in JSON format
- `--shows [filter]` - List all available shows, optionally filtered by name/slug

### Mover command
- `--directory, -d` - Series directory containing episode files
- `--slug, -s` - Anime show slug (e.g., 'naruto', 'dragon-ball')
- `--filler` - Move filler episodes
- `--mixed` - Move mixed canon/filler episodes

### General
- `--help` - Show help message
