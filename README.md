# Full-Text Search Engine for Websites

A Python project that crawls web pages, builds TF-IDF representations of their
text, stores the indexed documents in SQLite, and ranks search results using
cosine similarity.

## Features

- Crawl web pages by following links up to a configurable depth.
- Check a site's `robots.txt` before fetching pages.
- Calculate term frequency (TF) and inverse document frequency (IDF) with
  Apache Beam.
- Store document URLs and their TF-IDF representations in SQLite.
- Rank documents for a query using cosine similarity.

## Project structure

```text
app/
  check_db.py       # Print the indexed documents and their representations
  crawler.py        # Web crawler
  indekser.py       # Crawl pages, calculate TF-IDF, and save the index
  wyszukiwarka.py   # Search indexed documents
tests/
  test_crawler.py
  test_indekser.py
  test_wyszukiwarka.py
```

## Requirements

- Python
- Apache Beam
- Requests
- Beautiful Soup 4
- pytest (to run the tests)

Install the packages with pip:

```bash
python -m pip install apache-beam requests beautifulsoup4 pytest
```

## Build the search index

Run the indexer from the `app` directory. The crawler starts from the
Izanami and Izanagi Wikipedia page, and the SQLite database is created one
directory above the current working directory as `indeks.db`.

```bash
cd app
python indekser.py
```

The crawler needs an internet connection. The start URL, crawl depth, and
request delay can be changed in the `__main__` section of `app/indekser.py`.

## Search

After building the index, run the search script from the same `app` directory:

```bash
python wyszukiwarka.py
```

The current query is set in `app/wyszukiwarka.py`. Update the `text` value to
search for different terms. The script prints up to three top results by
cosine similarity.

## Inspect the database

With the working directory set to `app`, run:

```bash
python check_db.py
```

## Run tests

From the repository root, run:

```bash
python -m pytest
```

Crawler tests mock HTTP requests and delays, so they do not access the
internet.
