"""Story deduplication/clustering: groups raw articles that cover the same underlying
story into one canonical cluster (spec 12.4). Two interchangeable strategies:

- cluster_articles/is_same_story: headline similarity, keyword overlap, and named
  entity overlap. Pure functions -- no I/O -- unit-testable without network access, but
  brittle on real-world data where outlets phrase the same story very differently.
- cluster_by_embeddings: cosine similarity over precomputed embedding vectors (see
  llm.LLMClient.generate_embeddings). Also a pure function -- the network call happens
  in the caller, embeddings are passed in -- generalizes far better across differently
  worded headlines since it compares meaning rather than surface text.
"""
import math
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
        # Strip a trailing possessive ('s/s') before the punctuation strip below, so
        # "Arday's" and "Arday" are recognised as the same entity token.
        word = re.sub(r"['\u2019]s$", "", word)
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


def _cluster_by_pairwise_match(articles, is_match):
    """Shared union-find grouping: is_match(i, j) decides if articles[i]/articles[j]
    belong together. Transitive (A~B and B~C implies A~C~B), order preserved within
    each cluster.
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
            if is_match(i, j):
                union(i, j)

    clusters = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(articles[i])
    return list(clusters.values())


def cluster_articles(articles):
    """Groups articles into clusters of the same underlying story using the headline/
    keyword/entity heuristic (is_same_story). Returns a list of clusters, each a list
    of the original article dicts, in input order.
    """
    return _cluster_by_pairwise_match(articles, lambda i, j: is_same_story(articles[i], articles[j]))


def cosine_similarity(vector_a, vector_b):
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def cluster_by_embeddings(articles, embeddings, similarity_threshold=0.80):
    """Groups articles using cosine similarity between precomputed embedding vectors
    (one per article, same order -- see llm.LLMClient.generate_embeddings). Generalizes
    across differently-worded headlines much better than cluster_articles' surface-text
    heuristic, since it compares meaning rather than characters/keywords.

    0.80 default calibrated against a real day's RSS pull (~176 articles/5 sources):
    below ~0.78 starts merging same-topic-but-different-story pairs (e.g. an athletics
    editorial with a specific athlete's story); 0.80-0.85 cleanly caught only genuine
    same-story duplicates (same event covered by multiple outlets).
    """
    if len(embeddings) != len(articles):
        raise ValueError(f"expected {len(articles)} embeddings, got {len(embeddings)}")
    return _cluster_by_pairwise_match(
        articles, lambda i, j: cosine_similarity(embeddings[i], embeddings[j]) >= similarity_threshold
    )
