"""Utility functions for data processing and formatting."""

from difflib import SequenceMatcher

from anifiller.constants import SIMILARITY_THRESHOLD


def calculate_similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_similar_shows(query: str, shows: list[dict[str, str]], limit: int = 5) -> list[dict[str, str]]:
    """Find shows similar to the query string."""
    similarities = []

    for show in shows:
        # Check similarity with both name and slug
        name_similarity = calculate_similarity(query, show["name"])
        slug_similarity = calculate_similarity(query, show["slug"])

        # Use the higher similarity score
        max_similarity = max(name_similarity, slug_similarity)

        if max_similarity > SIMILARITY_THRESHOLD:  # Only include if similarity is above threshold
            similarities.append((max_similarity, show))

    # Sort by similarity (highest first) and return top matches
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [show for _, show in similarities[:limit]]


def parse_episode_ranges(text: str) -> list[int]:
    """Parse episode ranges like '1-28, 34-41, 43' into a list of episode numbers."""
    episodes: list[int] = []

    # Split by commas and clean up whitespace
    parts = [part.strip() for part in text.split(",")]

    for part in parts:
        if "-" in part:
            # Handle ranges like "1-28"
            start, end = map(int, part.split("-"))
            episodes.extend(range(start, end + 1))
        else:
            # Handle single episodes like "43"
            episodes.append(int(part))

    return episodes


def format_episode_list(episodes: list[int]) -> str:
    """Format a list of episodes into ranges where possible."""
    if not episodes:
        return "None"

    episodes = sorted(episodes)
    ranges = []
    start = episodes[0]
    end = episodes[0]

    for i in range(1, len(episodes)):
        if episodes[i] == end + 1:
            end = episodes[i]
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = end = episodes[i]

    # Add the last range
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")

    return ", ".join(ranges)


def filter_shows(all_shows: list[dict[str, str]], filter_term: str) -> list[dict[str, str]]:
    """Filter shows by name or slug containing the filter term (case insensitive)."""
    if not filter_term:
        return all_shows

    filter_lower = filter_term.lower()
    return [show for show in all_shows if filter_lower in show["name"].lower() or filter_lower in show["slug"].lower()]
