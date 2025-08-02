"""Output formatting functions for episode data."""

import json
import sys

import requests

from anifiller.exceptions import AnifillerError
from anifiller.scraper import scrape_available_shows
from anifiller.utils import filter_shows, find_similar_shows, format_episode_list


def handle_shows_command(filter_term: str | None) -> None:
    """Handle the --shows command."""
    all_shows = scrape_available_shows()
    shows = filter_shows(all_shows, filter_term or "")
    print(json.dumps(shows, indent=2))


def create_json_output(show_name: str, episode_data: dict[str, list[int]]) -> dict:
    """Create JSON output format."""
    return {
        "show_name": show_name,
        "manga_canon": episode_data["manga_canon"],
        "mixed_canon_filler": episode_data["mixed_canon_filler"],
        "filler": episode_data["filler"],
        "summary": {
            "canon_count": len(episode_data["manga_canon"]),
            "mixed_count": len(episode_data["mixed_canon_filler"]),
            "filler_count": len(episode_data["filler"]),
            "total_count": len(episode_data["manga_canon"])
            + len(episode_data["mixed_canon_filler"])
            + len(episode_data["filler"]),
        },
    }


def print_formatted_output(episode_data: dict[str, list[int]]) -> None:
    """Print episode data in formatted text output."""
    canon = format_episode_list(episode_data["manga_canon"])
    mixed = format_episode_list(episode_data["mixed_canon_filler"])
    filler = format_episode_list(episode_data["filler"])

    print(f"Canon: {canon}")
    print(f"Mixed: {mixed}")
    print(f"Filler: {filler}")


def suggest_similar_shows(show_name: str) -> None:
    """Suggest similar shows when a show is not found."""
    print("\nDid you mean one of these shows?", file=sys.stderr)
    try:
        all_shows = scrape_available_shows()
        similar_shows = find_similar_shows(show_name, all_shows)

        if similar_shows:
            for show in similar_shows:
                print(f"  {show['name']} (slug: {show['slug']})", file=sys.stderr)
            print(f"\nTry: anifiller list {similar_shows[0]['slug']}", file=sys.stderr)
        else:
            print("  No similar shows found. Use anifiller list --shows to see all available shows.", file=sys.stderr)
    except (AnifillerError, requests.RequestException):
        print("  Use anifiller list --shows to see all available shows.", file=sys.stderr)
