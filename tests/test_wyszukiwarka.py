import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


from app.wyszukiwarka import prepare_query, cosine_similarity


def test_prepare_query_standard():
    query = "Python jest szybki!"
    stopwords = {"jest"}

    result = prepare_query(query, stopwords)

    result_expected = {"python": 0.5, "szybki": 0.5}

    assert result == result_expected


def test_prepare_query_only_stopwords():

    query = "jest na"
    stopwords = {"jest", "na"}

    result = prepare_query(query, stopwords)

    assert result == None


def test_prepare_query_punctuaction():

    query = "??? Python, Python!!!"
    stopwords = {}

    result = prepare_query(query, stopwords)

    result_expected = {"python": 1}

    assert result == result_expected


def test_cosine_similarity_no_common_words():
    query = {"python": 0.5}
    doc = {"java": 0.8}

    assert cosine_similarity(query, doc) == 0.0


def test_cosine_similarity_empty_dict():
    query = {}
    doc = {"python": 0.5}

    assert cosine_similarity(query, doc) == 0.0
