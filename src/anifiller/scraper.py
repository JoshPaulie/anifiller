"""Web scraping functionality for animefillerlist.com."""

from typing import cast

import requests
from bs4 import BeautifulSoup, Tag

from anifiller.constants import BASE_URL, SHOWS_URL, USER_AGENT
from anifiller.exceptions import EpisodeInfoNotFoundError, ScrapingError, ShowsListNotFoundError
from anifiller.utils import parse_episode_ranges


def _parse_episodes_from_div(parent_div: Tag, class_name: str) -> list[int]:
    """Parse episode data from a specific div class."""
    target_div = parent_div.find("div", class_=class_name)
    if target_div and isinstance(target_div, Tag):
        episodes_span = target_div.find("span", class_="Episodes")
        if episodes_span and isinstance(episodes_span, Tag):
            episode_texts = [link.get_text() for link in episodes_span.find_all("a")]
            episode_ranges_text = ", ".join(episode_texts)
            return parse_episode_ranges(episode_ranges_text)
    return []


def _extract_shows_from_groups(show_groups: list) -> list[dict[str, str]]:
    """Extract show information from show groups."""
    shows = []
    for group in show_groups:
        if not isinstance(group, Tag):
            continue

        # Find all links in this group
        links = group.find_all("a", href=True)
        for link in links:
            if not isinstance(link, Tag):
                continue

            href = link.get("href")
            if not isinstance(href, str) or not href.startswith("/shows/"):
                continue

            # Extract show slug from URL
            show_slug = href.replace("/shows/", "")
            show_name = link.get_text(strip=True)
            shows.append(
                {
                    "name": show_name,
                    "slug": show_slug,
                },
            )
    return shows


def scrape_available_shows() -> list[dict[str, str]]:
    """Scrape all available shows from animefillerlist.com/shows."""
    try:
        response = requests.get(SHOWS_URL, timeout=10, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Error fetching shows list: {e}"
        raise ScrapingError(msg, e) from e

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        show_groups = soup.find_all("div", class_="Group")

        if not show_groups:
            raise ShowsListNotFoundError

        return _extract_shows_from_groups(show_groups)

    except ShowsListNotFoundError:
        raise
    except Exception as e:
        msg = f"Error parsing shows list: {e}"
        raise ScrapingError(msg, e) from e


def scrape_anime_episodes(show_name: str) -> dict[str, list[int]]:
    """Scrape episode information for a given anime show."""
    show_url = f"{BASE_URL}/shows/{show_name}"

    try:
        response = requests.get(show_url, timeout=10, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Error fetching data from {show_url}: {e}"
        raise ScrapingError(msg, e) from e

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        condensed_div = soup.find("div", id="Condensed")

        if not condensed_div or not isinstance(condensed_div, Tag):
            raise EpisodeInfoNotFoundError

        # Type cast for mypy - we know condensed_div is a Tag at this point
        condensed_div = cast("Tag", condensed_div)

        # Initialize result dictionary and parse all episode types
        return {
            "manga_canon": _parse_episodes_from_div(condensed_div, "manga_canon"),
            "mixed_canon_filler": _parse_episodes_from_div(condensed_div, "mixed_canon/filler"),
            "filler": _parse_episodes_from_div(condensed_div, "filler"),
        }

    except EpisodeInfoNotFoundError:
        raise
    except Exception as e:
        msg = f"Error parsing episode data: {e}"
        raise ScrapingError(msg, e) from e
