from infra.ec2.ingestion.clustering import cluster_articles


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
