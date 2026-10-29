import sqlite3
import ast
import math

STOPWORDS = {"jest", "i", "w", "na", "z", "a"}

def prepare_query(query_text,stopwords):

    prepared_words = []

    for word in query_text.split():
        cleaned_word = word.strip(".,!?").lower()
        if cleaned_word not in stopwords and cleaned_word != "":
            prepared_words.append(cleaned_word)

    words_len = len(prepared_words)
    if words_len > 0:
        count = {}
        for word in prepared_words:
            count[word] = count.get(word,0)+1

        

        tf_dict = {}
        for w,v in count.items():
            tf_dict[w] = v/words_len

        
        return tf_dict

def download_documents(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls_documents")
    documents = cursor.fetchall()
    conn.commit()
    conn.close()
    tfidf_dict = {}
    for document in documents:
        path = document[1]
        text = ast.literal_eval(document[2])
        tfidf_dict[path] = text
        

    return tfidf_dict

def dot_product(query_dict, document_dict):

    dot_product_sum = 0

    for query_w, query_v in query_dict.items():
        if query_w in document_dict:
            dot_product_sum += query_v * document_dict[query_w]

    return dot_product_sum

def vector_length(vector_dict):

    vector_sum = 0

    for vector_w,vector_v in vector_dict.items():
        
        vector_sum += vector_v * vector_v

    return float(math.sqrt(vector_sum))

def cosine_similarity(query_dict,document_dict):

    dot_product_result = dot_product(query_dict,document_dict)

    vector_query = vector_length(query_dict)
   
    vector_document = vector_length(document_dict)

    denominator = vector_query * vector_document

    if denominator == 0:
        return 0.0

    return dot_product_result/denominator
    

def search(query_text,db_path,top_n=3):

    prepared_text_query = prepare_query(query_text,STOPWORDS)

    prepared_list_documents = download_documents(db_path)

    list_probability = []
    for doc_w, doc_v in prepared_list_documents.items():
        cosine_sim = cosine_similarity(prepared_text_query,doc_v)
        list_probability.append((doc_w, cosine_sim))
    
    list_probability.sort(key=lambda x : x[1], reverse=True)

    top_results = list_probability[:top_n]

    print(f"Zapytanie: {query_text}")
    print("Odpowiedź:")
    for i, (path, score) in enumerate(top_results, start=1):    
        print(f"{i}: {path} (podobieństwo: {score:.4f})")

    
    return list_probability




# text = input("Wpisz tekst:")
text = "Python jest tak szybki że aż python"
# tf_dict = prepare_query(text,STOPWORDS)
search(text,"../indeks.db")