from django_wikipedia_connector.models.article import Article


def test_article_str():
    article = Article(title="foo")
    assert str(article) == "foo"
