import ast
import sqlite3
import sys
from pathlib import Path

import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "app"))

from app.indekser import TF, TFIDF_I_Save


def test_beam_clean_text_transform():
    input_data = [
        {
            "path_url": "https://pl.wikipedia.org/wiki/Shintō",
            "text": "Religia shinto jest religią występującą w Japonii.",
        }
    ]

    expected_output = [
        {
            "path_url": "https://pl.wikipedia.org/wiki/Shintō",
            "tf": {
                "religia": 1 / 5,
                "shinto": 1 / 5,
                "religią": 1 / 5,
                "występującą": 1 / 5,
                "japonii": 1 / 5,
            },
        }
    ]

    with TestPipeline() as pipeline:
        output = (
            pipeline
            | "CreateInput" >> beam.Create(input_data)
            | "ComputeTF" >> beam.ParDo(TF())
        )
        assert_that(output, equal_to(expected_output))


def test_tf_dofn_empty_text():
    input_data = [
        {
            "path_url": "https://pl.wikipedia.org/wiki/Shintō",
            "text": "jest i w na",
        }
    ]

    expected_output = [
        {
            "path_url": "https://pl.wikipedia.org/wiki/Shintō",
            "tf": {},
        }
    ]

    with TestPipeline() as pipeline:
        output = (
            pipeline
            | "CreateInput" >> beam.Create(input_data)
            | "ComputeTF" >> beam.ParDo(TF())
        )
        assert_that(output, equal_to(expected_output))


def test_tf_idf_i_save_dofn(tmp_path, monkeypatch):
    path_url = "https://example.com/docs/test"
    db_path = tmp_path / "indeks.db"

    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE urls_documents (
                url_id INTEGER PRIMARY KEY AUTOINCREMENT,
                path_url TEXT,
                representation TEXT
            )
            """)

    working_dir = tmp_path / "work"
    working_dir.mkdir()
    monkeypatch.chdir(working_dir)

    input_data = [
        {
            "path_url": path_url,
            "tf": {"python": 0.5, "szybki": 0.5},
        }
    ]

    with TestPipeline() as pipeline:
        main_input = pipeline | "CreateMain" >> beam.Create(input_data)
        total_docs = pipeline | "CreateTotal" >> beam.Create([2])
        df_counts = pipeline | "CreateDF" >> beam.Create([("python", 1), ("szybki", 2)])

        output = main_input | "SaveTFIDF" >> beam.ParDo(
            TFIDF_I_Save(),
            n_docs=beam.pvalue.AsSingleton(total_docs),
            df_dict=beam.pvalue.AsDict(df_counts),
        )

        assert_that(output, equal_to([path_url]))

    with sqlite3.connect(db_path) as connection:
        saved_url, representation = connection.execute(
            "SELECT path_url, representation FROM urls_documents"
        ).fetchone()

    assert saved_url == path_url
    assert ast.literal_eval(representation) == {
        "python": 0.3466,
        "szybki": 0.0,
    }
