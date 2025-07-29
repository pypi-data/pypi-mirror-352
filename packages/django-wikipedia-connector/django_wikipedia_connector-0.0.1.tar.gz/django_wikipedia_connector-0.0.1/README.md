# Django Wikipedia Connector #

The **Django Wikipedia Connector** is a Django app that can import a Wikipedia XML database dump into a database using
Django models. It was written to be used with the Greek Wikipedia XML dump, so it has the Greek word for "category"
harcoded in the code. If you want to use this for a different language, please open an issue and we can parametrise that
name.

## Installation ##

Install with `pip`:

```
pip install django-wikipedia-connector
```

## Import XML Dump ##

1.  Find the dump you want to work with at the [WikiMedia dumps backup index]. For example, for the Greek wikipedia dump
    dated 2025-05-01, the file was named `elwiki-20250501-pages-articles-multistream.xml.bz2` and it was 560.8 MB
    compressed.
2.  Extract. For that same example, the extracted file was name `elwiki-20250501-pages-articles-multistream.xml` and it
    was 3 GB uncompressed.
3.  With this app installed and migrations ran, you can import the dump with `./manage.py import_dump`, followed by the
    file path to the XML dump, e.g:

    ```
    ./manage.py import_dump /home/alice/elwiki-20250501-pages-articles-multistream.xml
    ```

### Import Options ###

By default, the code will first import all Categories, and then it will import all Articles and link each Article to its
Categories. Importing data to the database takes a lot of time, so you skip some imports, provided you understand the
consequences of skipping:

* Option `--skip-categories` will skip importing the categories. If you already have the categories in your database
  from a previous import, or you don't care about categories, you can save some time.
* Option `--skip-articles` will skip importing the articles. If you already have the articles in your database from a
  previous import, or you only care about categories, you can save some time.
* Option `--skip-categorisation` will skip linking Articles to their Categories. This is the most time consuming
  function of the code. If you are not interested in linking Articles to Categories, you can save a lot of time.

## Caveats ##

The code should have some way to delete pages from the database when they are deleted from the dump. This feature is not
yet available. The easiest way to work around this restriction is to manually truncate the `Article`, `Category` and
`ArticleCategory` tables in your database, prior to the import.

<!-- Links -->
[WikiMedia dumps backup index]: https://dumps.wikimedia.org/backup-index.html