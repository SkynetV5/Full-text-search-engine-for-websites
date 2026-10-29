import ast
import sqlite3

conn = sqlite3.connect("../indeks.db")
cursor = conn.cursor()

#Download data
cursor.execute("SELECT doc_id, path, representation FROM urls_documents")
rows = cursor.fetchall()

print(f"📊 Liczba zindeksowanych dokumentów: {len(rows)}\n")

#Preview documents
for url_id, path_url, representation in rows:
    print(f"📄 URL_ID: {url_id}")
    print(f"📁 Ścieżka_URL: {path_url}")

    # change type data to dict
    tfidf_dict = ast.literal_eval(representation)

    print("🔑 Wagi TF-IDF słów:")
    for word, value in tfidf_dict.items():
        print(f"   • {word}: {value}")
    print("-" * 40)

conn.close()