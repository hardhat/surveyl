import pytest

from infra.ec2.ingestion.clustering import cluster_articles, cluster_by_embeddings, cosine_similarity, extract_entities


def _article(headline, source="Test Source"):
    return {"headline": headline, "source": source}


def test_five_duplicate_headlines_cluster_into_one_story():
    articles = [
        _article("Chancellor announces surprise tax cut in budget"),
        _article("Chancellor unveils surprise tax cut in the budget"),
        _article("Surprise tax cut announced by the Chancellor in budget"),
        _article("Budget: Chancellor announces a surprise tax cut"),
        _article("Chancellor's surprise budget tax cut explained"),
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 1
    assert len(clusters[0]) == 5


def test_unrelated_headlines_stay_in_separate_clusters():
    articles = [
        _article("Chancellor announces surprise tax cut in budget"),
        _article("Manchester United sack manager after poor run of form"),
        _article("Storm warning issued for northern England this weekend"),
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 3


def test_transitive_clustering_links_a_to_c_via_b():
    articles = [
        _article("PM Rishi Sunak announces general election date"),
        _article("Rishi Sunak calls general election for July"),
        _article("General election date confirmed by Rishi Sunak"),
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 1
    assert len(clusters[0]) == 3


def test_extract_entities_matches_possessive_and_bare_form():
    # Regression test: "Arday's" used to be a distinct entity token from "Arday"
    # because .strip() only trims characters from the ends of a token, not internal
    # ones -- so two headlines about the same person failed to match on entity overlap.
    possessive = extract_entities("Jason Arday's family mourn his death")
    bare = extract_entities("Vigil held for Jason Arday")

    assert possessive & bare == {"Jason Arday"}


def test_cosine_similarity_identical_orthogonal_and_zero_vectors():
    assert cosine_similarity([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)
    assert cosine_similarity([1, 0, 0], [0, 1, 0]) == pytest.approx(0.0)
    assert cosine_similarity([0, 0, 0], [1, 0, 0]) == 0.0


def test_cluster_by_embeddings_groups_by_similarity_threshold():
    articles = [
        _article("Chancellor unveils surprise tax cut"),
        _article("Surprise budget tax cut announced by Chancellor"),
        _article("Manchester United sack manager after poor run of form"),
    ]
    # Near-identical embeddings for the two tax-cut articles, an orthogonal one for
    # the unrelated football story.
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.99, 0.14, 0.0],
        [0.0, 1.0, 0.0],
    ]

    clusters = cluster_by_embeddings(articles, embeddings, similarity_threshold=0.82)

    assert len(clusters) == 2
    assert {a["headline"] for a in clusters[0]} == {articles[0]["headline"], articles[1]["headline"]}
    assert clusters[1] == [articles[2]]


def test_cluster_by_embeddings_rejects_mismatched_lengths():
    articles = [_article("A"), _article("B")]

    with pytest.raises(ValueError):
        cluster_by_embeddings(articles, embeddings=[[1, 0]])
