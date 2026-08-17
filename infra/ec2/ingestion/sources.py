"""Raw story fetch job: pulls today's articles from the curated UK outlet whitelist via
public RSS feeds (spec 12.1/12.2). No API key required.
"""
import logging
from datetime import datetime, timedelta

import feedparser

from .config import SOURCE_WHITELIST, UK_TZ

logger = logging.getLogger(__name__)


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
        feed = feedparser.parse(feed_url)
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
