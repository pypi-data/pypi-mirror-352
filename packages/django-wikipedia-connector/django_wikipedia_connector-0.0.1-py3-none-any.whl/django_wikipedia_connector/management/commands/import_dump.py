import time
import xml.etree.ElementTree  # nosec
from typing import List

import defusedxml.ElementTree
import wikitextparser
from django.core.management.base import BaseCommand, CommandError

from django_wikipedia_connector.models import Article, Category, Page


def _get_tree(path: str) -> xml.etree.ElementTree.ElementTree:
    tree = defusedxml.ElementTree.parse(path)
    if not isinstance(tree, xml.etree.ElementTree.ElementTree):
        raise CommandError("Something went wrong: Could not parse Tree.")
    return tree


def _get_root(path: str) -> xml.etree.ElementTree.Element:
    tree = _get_tree(path)
    root = tree.getroot()
    if not isinstance(root, xml.etree.ElementTree.Element):
        raise CommandError("Something went wrong: Could not parse Root.")
    return root


def _get_pages(path: str) -> List[Page]:
    root = _get_root(path)

    pages = []
    for child in root:
        child_tag = child.tag.split("}")[1] if "}" in child.tag else child.tag
        if child_tag != "page":
            continue
        pages.append(Page(child))
    return pages


def import_categories(categories: List[Page]) -> None:
    start = time.time()
    i = 1
    num_categories = len(categories)
    for category in categories:
        instance, created = Category.objects.update_or_create(id=category.id, title=category.title, text=category.text)
        print(f"{i} of {num_categories}: {"Created" if created else "Updated"} instance {instance}")
        i += 1
    end = time.time()
    print(f"Imported {len(categories)} categories in {end - start} seconds.")


def import_articles(articles, skip_categorisation=False) -> None:
    start = time.time()
    i = 1
    num_articles = len(articles)
    for article in articles:
        instance, created = Article.objects.update_or_create(id=article.id, title=article.title, text=article.text)
        print(f"{i} of {num_articles}: {"Created" if created else "Updated"} instance {instance}")
        i += 1

        if not skip_categorisation:
            parsed_text = wikitextparser.parse(article.text)
            parsed_categories = [wl for wl in parsed_text.wikilinks if wl.title.split(":")[0].lower() == "κατηγορία"]

            for parsed_category in parsed_categories:
                parsed_category_title = parsed_category.title[0].upper() + parsed_category.title[1:]  # capitalise "K"
                try:
                    instance.categories.add(Category.objects.get(title=parsed_category_title))
                except Category.DoesNotExist:  # https://el.wikipedia.org/w/index.php?title=Ειδικό:ΕπιθυμητέςΚατηγορίες
                    continue

    end = time.time()
    print(f"Imported {len(articles)} articles in {end - start} seconds.")


class Command(BaseCommand):
    help = "Imports a Wikipedia database dump"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="The file path to the XML Wikipedia dump")
        parser.add_argument("--skip-categories", action="store_true", default=False, help="Skip importing categories")
        parser.add_argument("--skip-articles", action="store_true", default=False, help="Skip importing articles")
        parser.add_argument(
            "--skip-categorisation", action="store_true", default=False, help="Don't link articles to categories"
        )

    def handle(self, *args, **options):
        pages = _get_pages(options["path"])
        print(f"Found {len(pages)} pages.")

        if not options["skip_categories"]:
            categories = [page for page in pages if page.is_category]
            # On my laptop, the most important machine in the universe, importing the categories takes about 7 minutes:
            import_categories(categories)

        if not options["skip_articles"]:
            # On my laptop, the most important machine in the universe, importing the articles without categorisation
            # takes about 34 minutes, and importing with categorisation takes about 3 hours 10 minutes:
            articles = [page for page in pages if not page.is_category]
            import_articles(articles, options["skip_categorisation"])
