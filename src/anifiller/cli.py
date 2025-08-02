"""Command-line interface for the anifiller application."""

import argparse
import json
import sys

import requests

from anifiller.exceptions import AnifillerError, ScrapingError
from anifiller.scraper import scrape_anime_episodes, scrape_available_shows
from anifiller.utils import filter_shows, find_similar_shows, format_episode_list


def _create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    # Import here to avoid circular import
    from anifiller import __version__

    parser = argparse.ArgumentParser(
        description="Get anime episode information (canon, mixed, filler) from animefillerlist.com",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"anifiller {__version__}",
    )
    parser.add_argument(
        "show_name",
        nargs="?",
        help="The anime show name as it appears in the URL (e.g., 'dragon-ball', 'naruto')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output data in JSON format",
    )
    parser.add_argument(
        "--shows",
        nargs="?",
        const="",
        metavar="FILTER",
        help="List all available shows and exit. Optional filter to search for specific shows.",
    )
    return parser


def _handle_shows_command(filter_term: str | None) -> None:
    """Handle the --shows command."""
    all_shows = scrape_available_shows()
    shows = filter_shows(all_shows, filter_term or "")
    print(json.dumps(shows, indent=2))


def _create_json_output(show_name: str, episode_data: dict[str, list[int]]) -> dict:
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


def _print_formatted_output(episode_data: dict[str, list[int]]) -> None:
    """Print episode data in formatted text output."""
    canon = format_episode_list(episode_data["manga_canon"])
    mixed = format_episode_list(episode_data["mixed_canon_filler"])
    filler = format_episode_list(episode_data["filler"])

    print(f"Canon: {canon}")
    print(f"Mixed: {mixed}")
    print(f"Filler: {filler}")


def _suggest_similar_shows(show_name: str) -> None:
    """Suggest similar shows when a show is not found."""
    print("\nDid you mean one of these shows?", file=sys.stderr)
    try:
        all_shows = scrape_available_shows()
        similar_shows = find_similar_shows(show_name, all_shows)

        if similar_shows:
            for show in similar_shows:
                print(f"  {show['name']} (slug: {show['slug']})", file=sys.stderr)
            print(f"\nTry: anifiller {similar_shows[0]['slug']}", file=sys.stderr)
        else:
            print("  No similar shows found. Use --shows to see all available shows.", file=sys.stderr)
    except (AnifillerError, requests.RequestException):
        print("  Use --shows to see all available shows.", file=sys.stderr)


def main() -> None:
    """Run the main CLI function for the anifiller application."""
    parser = _create_parser()
    args = parser.parse_args()

    try:
        if args.shows is not None:
            _handle_shows_command(args.shows)
            return

        if not args.show_name:
            parser.error("show_name is required unless --shows is used")

        episode_data = scrape_anime_episodes(args.show_name)

        if args.json:
            output = _create_json_output(args.show_name, episode_data)
            print(json.dumps(output, indent=2))
        else:
            _print_formatted_output(episode_data)

    except AnifillerError as e:
        error_message = str(e)
        print(f"Error: {error_message}", file=sys.stderr)

        # If it's a 404 error (show not found), suggest similar shows
        if isinstance(e, ScrapingError) and "404 Client Error" in error_message and not args.shows:
            _suggest_similar_shows(args.show_name or "")

        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
