import math
import sqlite3
import apache_beam as beam
from apache_beam.io import fileio
import os
from crawler import SimpleCrawler

STOPWORDS = {"jest", "i", "w", "na", "z", "a"}


def read_file(readable_file):
    path = readable_file.metadata.path
    print(f"--> Odczytuję plik: {path}")
    return {"path": readable_file.metadata.path, "text": readable_file.read_utf8()}


def create_database():
    conn = sqlite3.connect("../indeks.db")
    cursor = conn.cursor()
    # cursor.execute("DROP TABLE IF EXISTS urls_documents")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS urls_documents (url_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "path_url TEXT, representation TEXT) "
    )
    conn.commit()
    conn.close()


class TF(beam.DoFn):
    def process(self, element):
        path = element["path_url"]
        text = element["text"]

        words = []
        for w in text.split():
            clean_word = w.strip(".,!?()").lower()
            clean_word = clean_word.replace("\n", "")
            clean_word = clean_word.replace("\r", "")
            clean_word = clean_word.replace("\t", "")
            if clean_word not in STOPWORDS and clean_word != "":
                words.append(clean_word)

        words_length = len(words)

        count = {}
        for w in words:
            count[w] = count.get(w, 0) + 1

        # tf_dict = {}
        # for w, v in count.items():
        #     tf_dict[w] = v/words_length
        tf_dict = {w: v / words_length for w, v in count.items()}
        yield {"path_url": path, "tf": tf_dict}


class TFIDF_I_Save(beam.DoFn):

    def process(self, element, n_docs, df_dict):
        path = element["path_url"]
        tf_map = element["tf"]

        tfidf_map = {}
        for word, tf in tf_map.items():
            df = df_dict.get(word, 1)

            idf = math.log(n_docs / df) if df > 0 else 0

            tfidf_map[word] = round(tf * idf, 4)

        conn = sqlite3.connect("../indeks.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO urls_documents (path_url, representation) values (?,?)",
            (path, str(tfidf_map)),
        )
        conn.commit()
        conn.close()

        yield path


if __name__ == "__main__":
    create_database()

    crawl = SimpleCrawler(
        url="https://pl.wikipedia.org/wiki/Izanami_i_Izanagi",
        depth=1,
        delay_limit=1,
    )
    downloaded_pages = crawl.crawl_url()
    for page in downloaded_pages:
        print(f"📄 Ścieżka_URL: {page['path_url']}")

    # import os
    # import glob

    # print("Katalog roboczy:", os.getcwd())
    # print("Znalezione pliki:", glob.glob("docs/*.txt"))

    with beam.Pipeline() as pipeline:
        parsed_pages = (
            pipeline
            | "1. Pobrane strony" >> beam.Create(downloaded_pages)
            | "2. Oblicz TF" >> beam.ParDo(TF())
        )

        total_pages = parsed_pages | "Count Pages" >> beam.combiners.Count.Globally()

        unique_words_per_doc = (
            parsed_pages
            | "Pobierz unikalne slowa"
            >> beam.Map(lambda doc: list(set(doc["tf"].keys())))
            | "Spłaszcz do listy słów" >> beam.FlatMap(lambda words: words)
        )

        df_counts = (
            unique_words_per_doc | "Zlicz DF" >> beam.combiners.Count.PerElement()
        )

        (
            parsed_pages
            | "Zapis do bazy"
            >> beam.ParDo(
                TFIDF_I_Save(),
                n_docs=beam.pvalue.AsSingleton(total_pages),
                df_dict=beam.pvalue.AsDict(df_counts),
            )
        )
