"""File system operations for episode files."""

import re
import shutil
import sys
from pathlib import Path

from anifiller.exceptions import AnifillerError


def find_episode_files(directory: str, episodes: list[int]) -> list[tuple[int, str]]:
    """Find episode files in directory that match the given episode numbers."""
    directory_path = Path(directory)
    if not directory_path.exists():
        msg = f"Directory does not exist: {directory}"
        raise AnifillerError(msg)

    found_files = []
    video_extensions = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"}

    for file_path in directory_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            # Try to extract episode number from filename
            # Look for patterns like "Episode 01", "1. First Episode", etc.
            # Prioritize "Episode X" format in titles over season/episode codes
            filename = file_path.stem
            episode_patterns = [
                r"- Episode (\d+)",  # S01E01 - Episode 1 Title (prioritize this)
                r"^(\d+)\.\s",  # 1. First Episode, 2. Second Episode
                r"(?:episode|ep)[\s._-]*(\d+)",  # Episode 01, Ep01 (but not SxxExx format)
                r"(\d+)",  # Just a number (fallback)
            ]

            for pattern in episode_patterns:
                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    try:
                        episode_num = int(match.group(1))
                        if episode_num in episodes:
                            found_files.append((episode_num, str(file_path)))
                            break  # Found a match, don't try other patterns
                    except ValueError:
                        continue

    # Sort by episode number for consistent display
    found_files.sort(key=lambda x: x[0])
    return found_files


def move_episodes_to_filler_folder(directory: str, episode_files: list[tuple[int, str]]) -> None:
    """Move episode files to a 'filler' subfolder."""
    if not episode_files:
        print("No episode files found to move.")
        return

    directory_path = Path(directory)
    filler_folder = directory_path / "filler"

    # Create filler folder if it doesn't exist
    filler_folder.mkdir(exist_ok=True)

    moved_count = 0
    for episode_num, file_path in episode_files:
        source_path = Path(file_path)
        destination_path = filler_folder / source_path.name

        try:
            shutil.move(str(source_path), str(destination_path))
            print(f"Moved episode {episode_num}: {source_path.name}")
            moved_count += 1
        except OSError as e:
            print(f"Error moving episode {episode_num} ({source_path.name}): {e}", file=sys.stderr)

    print(f"\nMoved {moved_count} episode(s) to the filler folder.")
