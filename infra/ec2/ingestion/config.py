"""Static configuration for the news ingestion pipeline: source whitelist, ranking
weights, and the daily timing schedule. Kept as plain data (no I/O) so it's trivially
testable and editable without touching pipeline logic.
"""
from zoneinfo import ZoneInfo

UK_TZ = ZoneInfo("Europe/London")

# Ingestion freezes at 3:30am UK time; the game publishes at 6:00am UK time.
# Both are wall-clock times in Europe/London, so BST/GMT is handled automatically
# by ZoneInfo (see infra/ec2/crontab, which sets CRON_TZ=Europe/London to match).
INGESTION_FREEZE_HOUR = 3
INGESTION_FREEZE_MINUTE = 30
PUBLISH_HOUR = 6
PUBLISH_MINUTE = 0

# Curated whitelist of major UK national news outlets (public RSS feeds, no API key
# required). Flexible source count per spec 12.2 -- add/remove entries freely.
SOURCE_WHITELIST = {
    "BBC News": "https://feeds.bbci.co.uk/news/uk/rss.xml",
    "The Guardian": "https://www.theguardian.com/uk/rss",
    "Sky News": "https://feeds.skynews.com/feeds/rss/uk.xml",
    "The Independent": "https://www.independent.co.uk/news/uk/rss",
    "The Telegraph": "https://www.telegraph.co.uk/news/rss.xml",
    "ITV News": "https://www.itv.com/news/index.rss",
    "Reuters UK": "https://www.reuters.com/world/uk/rss",
}

# Ranking signal priority per spec 12.3: coverage volume > search spikes > social
# engagement. Weights are relative, not required to sum to 1.
RANKING_WEIGHTS = {
    "coverage_volume": 0.6,
    "search_spike": 0.3,
    "social_engagement": 0.1,
}

ROUND1_CANDIDATE_COUNT = 12
ROUND1_CORRECT_COUNT = 5
ROUND1_DECOY_COUNT = ROUND1_CANDIDATE_COUNT - ROUND1_CORRECT_COUNT

ROUND3_STORY_COUNT = 5
ROUND3_CANDIDATES_PER_STORY = 3
