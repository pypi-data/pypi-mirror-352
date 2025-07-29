from django_wikipedia_connector.models.category import Category


def test_category_str():
    category = Category(title="foo")
    assert str(category) == "foo"
