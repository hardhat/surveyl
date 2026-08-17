"""Search-spike and social-engagement signals used by ranking.py (spec 12.3).

Coverage volume is derived directly from clustered raw_stories counts (see
clustering.py); it needs no external service. The two signals here are lower priority
and depend on third-party services:

- search_spike: real Google Trends data via pytrends (unofficial API, no key required).
- social_engagement: a stubbed neutral placeholder for V1. No social API is wired up yet
  (Reddit/X/Bluesky all need their own app registration and rate-limit handling); every
  story gets the same neutral score so it doesn't skew ranking until a real source is
  wired in, and the 10% weight keeps its influence small either way.
"""
import logging

logger = logging.getLogger(__name__)

SOCIAL_ENGAGEMENT_STUB_VALUE = 0.0


def search_spike_score(query, timeframe="now 1-d", geo="GB"):
    """0-100 relative search interest for `query` over the given window, per Google
    Trends. Returns 0.0 on any failure (network, rate limit, no data, or timeout)
    rather than raising, since this is a best-effort secondary ranking signal.
    """
    try:
        from pytrends.request import TrendReq

        # (connect, read) timeout -- pytrends/requests has no default, so a stalled
        # connection would otherwise hang this call (and the whole ingestion run).
        pytrends = TrendReq(hl="en-GB", tz=0, timeout=(5, 10))
        pytrends.build_payload([query], timeframe=timeframe, geo=geo)
        data = pytrends.interest_over_time()
        if data.empty:
            return 0.0
        return float(data[query].mean())
    except Exception:  # pragma: no cover - network/service dependent
        logger.exception("search_spike_score failed for query=%r", query)
        return 0.0


def social_engagement_score(_story):
    """Stub for V1; see module docstring. Takes the story dict for a future real
    implementation's sake, but currently ignores it.
    """
    return SOCIAL_ENGAGEMENT_STUB_VALUE
