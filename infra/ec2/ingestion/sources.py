"""Raw story fetch job: pulls today's articles from the curated UK outlet whitelist via
public RSS feeds (spec 12.1/12.2). No API key required.
"""
import logging
from datetime import datetime, timedelta

import feedparser
import requests

from .config import SOURCE_WHITELIST, UK_TZ

logger = logging.getLogger(__name__)

FEED_FETCH_TIMEOUT_SECONDS = 10
# Some outlets block requests without a browser-like User-Agent (seen: 401/403/405
# from a bare "python-requests" UA even on otherwise-public RSS feeds).
FEED_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 SurveyleIngestionBot/1.0"
    )
}


def _entry_published_at(entry):
    for field in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, field, None)
        if parsed:
            return datetime(*parsed[:6], tzinfo=UK_TZ)
    return None


def fetch_raw_articles(news_window_start, news_window_end, sources=None):
    """Fetches articles published within [news_window_start, news_window_end) from
    every whitelisted source. Only pulls from SOURCE_WHITELIST (or the provided
    `sources` override) -- never anything outside that curated list.

    Returns a list of dicts ready to insert into raw_stories (minus canonical_story_id,
    which is assigned later by clustering).
    """
    sources = sources if sources is not None else SOURCE_WHITELIST
    articles = []
    for source_name, feed_url in sources.items():
        try:
            response = requests.get(
                feed_url, timeout=FEED_FETCH_TIMEOUT_SECONDS, headers=FEED_FETCH_HEADERS
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("feed fetch failed for %s (%s): %s", source_name, feed_url, exc)
            continue

        # feedparser.parse() never touches the network here -- we already fetched the
        # bytes above with a timeout, since feedparser's own fetch has none and can hang.
        feed = feedparser.parse(response.content)
        if feed.bozo:
            logger.warning("feed error for %s (%s): %s", source_name, feed_url, feed.bozo_exception)
            continue
        for entry in feed.entries:
            published_at = _entry_published_at(entry)
            if published_at is None or not (news_window_start <= published_at < news_window_end):
                continue
            articles.append(
                {
                    "source": source_name,
                    "source_url": entry.get("link"),
                    "headline": entry.get("title", "").strip(),
                    "article_text": entry.get("summary", ""),
                    "published_at": published_at.isoformat(),
                }
            )
    return articles


def news_window_for_game_date(game_date):
    """Spec 5.2: the strict previous-day news window for a given game_date."""
    window_start = datetime.combine(game_date - timedelta(days=1), datetime.min.time(), tzinfo=UK_TZ)
    window_end = datetime.combine(game_date, datetime.min.time(), tzinfo=UK_TZ)
    return window_start, window_end


def write_raw_articles(db, articles):
    if not articles:
        return []
    return db.insert("raw_stories", articles)
