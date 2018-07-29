from collections import defaultdict
import ssl
import time
import requests
from math import log, sqrt
import nltk
# nltk.download('punkt')

inverted_index = defaultdict(list)
# TODO no scarability
SOURCE_PATH = './sampledata/cpl1.0.txt'
num_of_documents = 1
vects_for_docs = []
document_freq_vect = {}

print('this is entry')

# TODO if db exists, not to index use exist db


def get_tokenized_normalized_token_list(text):
    tokens = nltk.word_tokenize(text)
    ps = nltk.stem.PorterStemmer()
    stemmedtokens = []
    for word in tokens:
        stemmedtokens.append(ps.stem(word))
    return stemmedtokens


"""
make vector from token list
document_freq_vect is the list of word appearing frequency through all doc
"""


def generate_vector(tokens):
    vect = {}
    global document_freq_vect  # TODO ここでgrobal宣言はいいのか？

    for token in tokens:
        if token in vect:  # TODO token分毎回アクセス効率悪くないかな
            vect[token] += 1
        else:
            vect[token] = 1
            if token in document_freq_vect:  # TODO token分毎回アクセス効率悪くないかな
                document_freq_vect[token] += 1
            else:
                document_freq_vect[token] = 1
    return vect


def generate_vector_in_search(queries):
    vect = {}
    for token in queries:
        if token in vect:
            vect[token] += 1.0
        else:
            vect[token] = 1.0
    return vect


"""
first, vects_for_docs is no duplicate key then 
key should have a word which is not duplicated
This is providing number for index
"""


def generate_inverted_index():
    count = 0
    for vector in vects_for_docs:
        for word in vector:
            inverted_index[word].append(count)
        count += 1


"""
term frequency - inverse document frequency
T = the times how many token appears in a document
A = the number of documents
D = the number of appearing a specific token
tf-idf = T * logA/D
or tf-idf = 1 + log(T) * logA/D ( if you have super long document )

vect[word] has the number how many times word in a document initially
in the end, vect[word] will have score of tf-idf

"""


def create_tf_idf_vector():
    vect_len = 0.0
    for vect in vects_for_docs:
        for word in vect:
            word_freq = vect[word]
            tmp = calc_tf_idf(word, word_freq)
            vect[word] = tmp  # TODO vectの状態かえてて気持ち悪い
            vect_len += tmp ** 2
        
        vect_len = sqrt(vect_len)
        for word in vect:
            if(vect_len != 0.0):
                vect[word] /= vect_len  # TODO vectの状態かえてて気持ち悪い


"""
if query token doen't have in freq_list, 
we can create additional tf-idf score from query

"""


def get_tf_idf_score(query_vector):
    vect_len = 0.0
    for word in query_vector:
        word_freq = query_vector[word]
        if word in document_freq_vect:
            # TODO query_vectorの状態かえてて気持ち悪い
            query_vector[word] = calc_tf_idf(word, word_freq)
        else:
            # TODO query_vectorの状態かえてて気持ち悪い
            query_vector[word] = (1 + log(word_freq)) * \
             log(num_of_documents / 1)
            vect_len += query_vector[word] ** 2
    vect_len = sqrt(vect_len)
    if vect_len != 0:
        for word in query_vector:
            query_vector[word] /= vect_len  # TODO query_vectorの状態かえてて気持ち悪い


def calc_tf_idf(word, word_freq):
    return (1 + log(word_freq)) * \
            log(num_of_documents / document_freq_vect[word])


"""
return score by adding token that has indexing vector list
"""


def get_sum_score(vector1, vector2):
    if len(vector1) > len(vector2):
        tmp = vector1
        vector1 = vector2
        vector2 = tmp
    keys1 = vector1.keys()
    keys2 = vector2.keys()
    sum = 0
    for i in keys1:
        if i in keys2:
            sum += vector1[i] * vector2[i]
    return sum


"""
return document sorted by sum score 
"""


def get_result_from_query_vect(query_vector):
    result = []
    sorted_result = []
    for i in range(num_of_documents):  # TODO なぜ-1??
        # TODO docIDごとにvect入ってるのをわかりやすく
        sum_score = get_sum_score(query_vector, vects_for_docs[i])
        result.append((i, sum_score))
        sorted_result = sorted(result, key=lambda x: x[1])  # TODO 効率チェック
    return sorted_result


print('start')
for i in range(num_of_documents):
    f = open(SOURCE_PATH, 'r')
    try:
        document = f.read()  # ほんとは一気readいくない負荷高め
        # TODO 圧縮メソッド
        token_list = get_tokenized_normalized_token_list(document)
        vect = generate_vector(token_list)
        vects_for_docs.append(vect)
    except UnicodeDecodeError:
        print("ERROR unicode decode")
    except requests.exceptions.ConnectionError:
        time.sleep(2)
    except requests.exceptions.Timeout:
        time.sleep(2)
    except ssl.SSLError:

        if vects_for_docs == {}:
            print("ERROR : vect is empty")
        else:
            generate_inverted_index() 

create_tf_idf_vector()

print("This is nitamon search")
while True:
    query = input("Enter input")
    if len(query) == 0:
        break
    query_list = get_tokenized_normalized_token_list(query)
    q_vect = generate_vector_in_search(query_list)
    get_tf_idf_score(q_vect)
    result = get_result_from_query_vect(q_vect)

    for tup in result:
        print("The document id = " + str(tup[0]).zfill(4) + " the"
              " score weight is " + str(tup[1]))
