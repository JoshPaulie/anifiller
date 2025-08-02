"""List command handler for the anifiller CLI."""

import argparse
import json
import sys

from anifiller.output_formatters import create_json_output, handle_shows_command, print_formatted_output
from anifiller.scraper import scrape_anime_episodes


def handle_list_command(args: argparse.Namespace) -> None:
    """Handle the list command (original functionality)."""
    if args.shows is not None:
        handle_shows_command(args.shows)
        return

    if not args.show_name:
        print("Error: show_name is required for the list command", file=sys.stderr)
        sys.exit(1)

    episode_data = scrape_anime_episodes(args.show_name)

    if args.json:
        output = create_json_output(args.show_name, episode_data)
        print(json.dumps(output, indent=2))
    else:
        print_formatted_output(episode_data)
