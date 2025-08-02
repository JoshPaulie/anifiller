"""Command-line interface for the anifiller application."""

import argparse
import sys

from anifiller.commands import handle_list_command, handle_mover_command
from anifiller.exceptions import AnifillerError, ScrapingError
from anifiller.output_formatters import suggest_similar_shows


def _create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    # Import here to avoid circular import
    from anifiller import __version__  # noqa: PLC0415

    parser = argparse.ArgumentParser(
        description="Get anime episode information (canon, mixed, filler) from animefillerlist.com",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"anifiller {__version__}",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command (current functionality)
    list_parser = subparsers.add_parser("list", help="List anime episode information")
    list_parser.add_argument(
        "show_name",
        nargs="?",
        help="The anime show name as it appears in the URL (e.g., 'dragon-ball', 'naruto')",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Output data in JSON format",
    )
    list_parser.add_argument(
        "--shows",
        nargs="?",
        const="",
        metavar="FILTER",
        help="List all available shows and exit. Optional filter to search for specific shows.",
    )

    # Mover command (new functionality)
    mover_parser = subparsers.add_parser("mover", help="Move filler/mixed episodes to a filler folder")
    mover_parser.add_argument(
        "--directory",
        "-d",
        required=True,
        help="Series directory containing episode files",
    )
    mover_parser.add_argument(
        "--slug",
        "-s",
        required=True,
        help="Anime show slug (e.g., 'dragon-ball', 'naruto')",
    )
    mover_parser.add_argument(
        "--filler",
        action="store_true",
        help="Move filler episodes",
    )
    mover_parser.add_argument(
        "--mixed",
        action="store_true",
        help="Move mixed canon/filler episodes",
    )
    mover_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without actually moving files",
    )

    return parser


def main() -> None:
    """Run the main CLI function for the anifiller application."""
    parser = _create_parser()
    args = parser.parse_args()

    try:
        # Handle different commands
        if args.command == "list":
            handle_list_command(args)
        elif args.command == "mover":
            handle_mover_command(args)
        else:
            # No command specified, show help
            parser.print_help()
            sys.exit(1)

    except AnifillerError as e:
        error_message = str(e)
        print(f"Error: {error_message}", file=sys.stderr)

        # If it's a 404 error (show not found), suggest similar shows
        if isinstance(e, ScrapingError) and "404 Client Error" in error_message:
            show_name = getattr(args, "show_name", None) or getattr(args, "slug", "")
            if show_name:
                suggest_similar_shows(show_name)

        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
