import xml.etree.ElementTree  # nosec
from unittest import mock

import pytest
from django.core.management.base import CommandError

from django_wikipedia_connector.management.commands.import_dump import (
    _get_pages,
    _get_root,
    _get_tree,
    import_categories,
)
from django_wikipedia_connector.models import Category, Page


@mock.patch("django_wikipedia_connector.management.commands.import_dump.defusedxml.ElementTree")
def test_get_tree(mock_element_tree):
    # setup
    fake_tree = xml.etree.ElementTree.ElementTree()
    mock_element_tree.parse.return_value = fake_tree

    # run
    tree = _get_tree("fake-path")

    # assert
    mock_element_tree.parse.assert_called_once_with("fake-path")
    assert tree == fake_tree


@mock.patch("django_wikipedia_connector.management.commands.import_dump.defusedxml.ElementTree")
def test_get_tree_raises(mock_element_tree):
    # setup
    mock_element_tree.parse.return_value = "this is not an XML element"

    # test
    with pytest.raises(CommandError) as exc:
        _get_tree("fake-path")
    assert str(exc.value) == "Something went wrong: Could not parse Tree."


@mock.patch("django_wikipedia_connector.management.commands.import_dump._get_tree")
def test_get_root(mock_get_tree):
    # setup
    fake_root = xml.etree.ElementTree.Element("root")
    fake_tree = xml.etree.ElementTree.ElementTree(fake_root)
    mock_get_tree.return_value = fake_tree

    # run
    root = _get_root("fake-path")

    # assert
    mock_get_tree.assert_called_once_with("fake-path")
    assert root == fake_root


@mock.patch("django_wikipedia_connector.management.commands.import_dump._get_tree")
def test_get_root_raises(mock_get_tree):
    # setup
    mock_get_tree.return_value = xml.etree.ElementTree.ElementTree()  # fake tree without root causes an exception

    with pytest.raises(CommandError):
        _get_root("fake-path")


@mock.patch("django_wikipedia_connector.management.commands.import_dump._get_root")
def test_get_pages(mock_get_root):
    # setup
    fake_root = xml.etree.ElementTree.Element("root")
    xml.etree.ElementTree.SubElement(fake_root, "page")
    xml.etree.ElementTree.SubElement(fake_root, "page")
    xml.etree.ElementTree.SubElement(fake_root, "not-page")
    mock_get_root.return_value = fake_root

    # run
    pages = _get_pages("fake-path")

    # assert
    mock_get_root.assert_called_once_with("fake-path")
    assert len(pages) == 2


@mock.patch.object(Page, "parse")
@pytest.mark.django_db
def test_import_categories(mock_page_parse):
    # pre...assert?
    assert Category.objects.count() == 0  # there are 0 categories before the import

    # setup
    fake_root = xml.etree.ElementTree.Element("root")
    fake_page = xml.etree.ElementTree.SubElement(fake_root, "page")

    fake_category_1 = Page(fake_page)
    fake_category_1.id = "1"
    fake_category_1.title = "Fake Title 1"
    fake_category_1.text = "Fake Text 1"
    fake_category_2 = Page(fake_page)
    fake_category_2.id = "2"
    fake_category_2.title = "Fake Title 2"
    fake_category_2.text = "Fake Text 2"

    # run
    import_categories([fake_category_1, fake_category_2])

    # assert
    assert Category.objects.count() == 2
