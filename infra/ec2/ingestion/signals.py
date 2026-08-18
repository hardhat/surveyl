"""Search-spike and social-engagement signals used by ranking.py (spec 12.3).

Coverage volume is derived directly from clustered raw_stories counts (see
clustering.py); it needs no external service. The two signals here are lower priority
and depend on third-party services:

- search_spike: real Google Trends data via SerpApi's Google Trends API (a paid proxy
  in front of Google Trends -- more reliable in a server/cron context than scraping
  Google Trends directly, which tends to get IP-blocked/CAPTCHA'd).
- social_engagement: a stubbed neutral placeholder for V1. No social API is wired up yet
  (Reddit/X/Bluesky all need their own app registration and rate-limit handling); every
  story gets the same neutral score so it doesn't skew ranking until a real source is
  wired in, and the 10% weight keeps its influence small either way.
"""
import logging

import requests

from .db import load_env

logger = logging.getLogger(__name__)

SOCIAL_ENGAGEMENT_STUB_VALUE = 0.0

SERPAPI_URL = "https://serpapi.com/search"
SERPAPI_TIMEOUT_SECONDS = 15


def search_spike_score(query, date="now 1-d", geo="GB", api_key=None):
    """0-100 relative search interest for `query` over the given window, per
    SerpApi's Google Trends API. Returns 0.0 on any failure (network, rate limit, no
    data, missing key, or timeout) rather than raising, since this is a best-effort
    secondary ranking signal.
    """
    # Same /etc/surveyle/surveyle.env convention as SupabaseClient.from_env()/LLMClient,
    # rather than reading os.environ directly (that missed the env file entirely).
    env = load_env()
    api_key = api_key or env.get("SERPAPI_API_KEY") or env.get("PYTRENDS_API_KEY")
    if not api_key:
        logger.warning("search_spike_score: no SerpApi key configured, returning 0.0")
        return 0.0

    params = {
        "engine": "google_trends",
        "q": query,
        "data_type": "TIMESERIES",
        "geo": geo,
        "date": date,
        "api_key": api_key,
    }
    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=SERPAPI_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        logger.exception("search_spike_score failed for query=%r", query)
        return 0.0

    interest = data.get("interest_over_time", {})

    averages = interest.get("averages") or []
    for entry in averages:
        if entry.get("query") == query and "value" in entry:
            return float(entry["value"])

    timeline = interest.get("timeline_data") or []
    values = []
    for point in timeline:
        for value_entry in point.get("values", []):
            if value_entry.get("query") == query and "extracted_value" in value_entry:
                values.append(float(value_entry["extracted_value"]))
    if values:
        return sum(values) / len(values)

    logger.warning("search_spike_score: no usable data in SerpApi response for query=%r", query)
    return 0.0



def social_engagement_score(_story):
    """Stub for V1; see module docstring. Takes the story dict for a future real
    implementation's sake, but currently ignores it.
    """
    return SOCIAL_ENGAGEMENT_STUB_VALUE
