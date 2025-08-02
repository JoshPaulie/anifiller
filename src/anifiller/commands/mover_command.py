"""Mover command handler for the anifiller CLI."""

import argparse
import sys
from pathlib import Path

from anifiller.file_operations import find_episode_files, move_episodes_to_filler_folder
from anifiller.scraper import scrape_anime_episodes


def handle_mover_command(args: argparse.Namespace) -> None:
    """Handle the mover command."""
    if not args.filler and not args.mixed:
        print("Error: At least one of --filler or --mixed must be specified.", file=sys.stderr)
        sys.exit(1)

    # Get episode data for the show
    episode_data = scrape_anime_episodes(args.slug)

    episodes_to_move = []
    if args.filler:
        episodes_to_move.extend(episode_data["filler"])
        print(f"Including {len(episode_data['filler'])} filler episodes")

    if args.mixed:
        episodes_to_move.extend(episode_data["mixed_canon_filler"])
        print(f"Including {len(episode_data['mixed_canon_filler'])} mixed canon/filler episodes")

    if not episodes_to_move:
        print("No episodes to move for the specified criteria.")
        return

    print(f"Looking for {len(episodes_to_move)} episode(s) in directory: {args.directory}")

    # Find matching files in the directory
    episode_files = find_episode_files(args.directory, episodes_to_move)

    if not episode_files:
        print("No matching episode files found in the directory.")
        print("Make sure the episode files have recognizable episode numbers in their filenames.")
        return

    print(f"Found {len(episode_files)} matching episode file(s):")
    for episode_num, file_path in episode_files:
        print(f"  Episode {episode_num}: {Path(file_path).name}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would move {len(episode_files)} episode(s) to the filler folder.")
        print("Use the command without --dry-run to actually move the files.")
        return

    # Ask for confirmation
    response = input("\nDo you want to move these files to the filler folder? (y/N): ")
    if response.lower() in ["y", "yes"]:
        move_episodes_to_filler_folder(args.directory, episode_files)
    else:
        print("Operation cancelled.")
