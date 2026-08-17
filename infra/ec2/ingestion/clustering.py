"""Story deduplication/clustering: groups raw articles that cover the same underlying
story into one canonical cluster, using headline similarity, keyword overlap, and named
entity overlap (spec 12.4). Pure functions -- no I/O -- so they're unit-testable without
a live database or network access.
"""
import re
from difflib import SequenceMatcher

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at", "to", "for", "with",
    "as", "is", "are", "was", "were", "be", "been", "being", "it", "its", "this", "that",
    "by", "from", "up", "down", "over", "after", "before", "than", "into", "out", "about",
    "will", "has", "have", "had", "not", "no", "amid", "amid", "says", "say", "said",
}

_WORD_RE = re.compile(r"[A-Za-z0-9']+")


def _tokens(text):
    return [w.lower() for w in _WORD_RE.findall(text)]


def extract_keywords(text):
    """Significant lowercase tokens, stopwords removed. Used for keyword-overlap scoring."""
    return {t for t in _tokens(text) if t not in _STOPWORDS and len(t) > 2}


def extract_entities(text):
    """Heuristic named-entity proxy: runs of capitalized words (e.g. "Rishi Sunak",
    "Manchester United"). No NLP dependency; good enough to compare headlines about the
    same people/places/organisations.
    """
    words = text.split()
    entities = set()
    current = []
    for word in words:
        cleaned = word.strip(".,:;!?\"'()")
        if cleaned and cleaned[0].isupper() and not cleaned.isupper():
            current.append(cleaned)
        else:
            if len(current) >= 1:
                entities.add(" ".join(current))
            current = []
    if len(current) >= 1:
        entities.add(" ".join(current))
    return entities


def headline_similarity(headline_a, headline_b):
    """Character-level similarity ratio (0-1) via difflib, case-insensitive."""
    return SequenceMatcher(None, headline_a.lower(), headline_b.lower()).ratio()


def _jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def is_same_story(article_a, article_b, similarity_threshold=0.55, keyword_threshold=0.4):
    """True if two articles are likely covering the same underlying story."""
    sim = headline_similarity(article_a["headline"], article_b["headline"])
    if sim >= similarity_threshold:
        return True

    keywords_a = extract_keywords(article_a["headline"])
    keywords_b = extract_keywords(article_b["headline"])
    keyword_overlap = _jaccard(keywords_a, keywords_b)

    entities_a = extract_entities(article_a["headline"])
    entities_b = extract_entities(article_b["headline"])
    shares_entity = bool(entities_a & entities_b)

    return keyword_overlap >= keyword_threshold and shares_entity


def cluster_articles(articles):
    """Groups articles into clusters of the same underlying story.

    Returns a list of clusters, each a list of the original article dicts, in input order.
    Uses simple union-find so clustering is transitive (A~B and B~C implies A~C~B).
    """
    n = len(articles)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(n):
        for j in range(i + 1, n):
            if is_same_story(articles[i], articles[j]):
                union(i, j)

    clusters = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(articles[i])
    return list(clusters.values())
