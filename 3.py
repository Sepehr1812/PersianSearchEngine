""" This project is implementation of a search engine with Information Retrieval principles on some Persian docs """
import re
from glob import glob
from math import sqrt, log10
from os import walk


class InvertedIndex:
    """
    Inverted Index class that contains a word and list of docs that include that word
    """

    def __init__(self, word: str, doc_no: int):
        self.word: str = word
        # the first argument is doc no, the second one is tf, the third one is weight, the fourth one is cluster number
        self.docs: list[(int, int, float)] = [(doc_no, 1, 0)]
        self.idf: float = 0.0

    def calculate_weights(self):
        """
        calculates weights of term self.word in different docs
        """
        for i in range(len(self.docs)):
            doc = self.docs[i]
            self.docs[i] = (doc[0], doc[1], (1 + log10(doc[1])) * log10(self.idf))


class ChampionList:
    """
    Champion List class contains a term and its champion docs
    """

    def __init__(self, word: str, docs: list[int]):
        self.word = word
        self.docs = docs


def stemming(word: str):
    """
    stemming the input word by five different method
    :return: stemmed word, empty string if the word should be removed

    """
    result = word.replace("ي", "ی")  # replace all ي (Arabic) with ی (Persian)

    result = re.compile("[^آ-ی]").sub("", result)  # remove all non-Persian-letter characters

    # remove conjugation of three auxiliary verbs: خواه، بود، باش
    if result == "خواهم" or result == "خواهی" or result == "خواهد" or result == "خواهیم" or result == "خواهید" or \
            result == "خواهند" or result == "بودم" or result == "بودی" or result == "بود" or result == "بودیم" or \
            result == "بودید" or result == "بودند" or result == "باشم" or result == "باشی" or result == "باشد" or \
            result == "باشیم" or result == "باشید" or result == "باشند":
        return ""

    # remove plural sign ها
    result = result.removesuffix('ها')
    result = result.removesuffix('های')

    # check if the word length is more than 4 to avoid changing data after removing superiority sign تر
    if len(result) > 4:
        result = result.removesuffix('تر')  # remove superiority sign تر

    return result


def create_inverted_index_list():
    """
    creates an inverted index list from docs in SampleDocs folder
    :return: inverted index list, number of docs and all docs
    """
    inverted_index_list: list[InvertedIndex] = []

    # collecting files
    clusters_num = 0
    for _, d, _ in walk("F:/Uni/7/IR/HW/Project/SampleDocs2"):
        clusters_num += len(d)  # calculating clusters number

    docs = []  # address of all docs
    doc_num = 0  # number of all docs
    for i in range(clusters_num):
        docs.append(glob(r'F:/Uni/7/IR/HW/Project/SampleDocs2/' + str(i) + '/*.txt'))
        doc_num += len(docs[i])

    # creating inverted list
    for i in range(len(docs)):
        for j in range(len(docs[i])):
            with open(docs[i][j], "r", encoding='utf-8') as f:
                sentences = [re.split("\\s+", line.rstrip('\n')) for line in f]
                for sentence in sentences:
                    for word in sentence:
                        stemmed_word = stemming(word)
                        if not stemmed_word == "":  # check if there is a non-empty string as stemmed word
                            # calculating number of doc
                            doc_no = i * len(docs[i]) + j + 1

                            for ii in inverted_index_list:
                                if ii.word.__eq__(stemmed_word):
                                    if not [x[0] for x in ii.docs].__contains__(doc_no):
                                        ii.docs.append((doc_no, 1))
                                    else:
                                        # increasing tf
                                        for k in range(len(ii.docs)):
                                            if ii.docs[k][0] == doc_no:
                                                ii.docs[k] = (doc_no, ii.docs[k][1] + 1)
                                                break
                                    break
                            else:
                                inverted_index_list.append(InvertedIndex(stemmed_word, doc_no))

    # calculating idf and weights
    for ii in inverted_index_list:
        ii.idf = doc_num / len(ii.docs)
        ii.calculate_weights()

    inverted_index_list = remove_over_repeated_words(inverted_index_list, doc_num)  # index elimination

    return inverted_index_list, doc_num, docs


def remove_over_repeated_words(inverted_index_list: list[InvertedIndex], docs_num: int):
    """
    removed all words that there are in more than %70 of all docs and their lengths are less than 4
    :param docs_num: number of all docs
    :return: filtered inverted index
    """
    return list(filter(lambda ii: len(ii.docs) < docs_num * 0.7 or len(ii.word) >= 5, inverted_index_list))


def create_champion_lists(inverted_index_list: list[InvertedIndex], r: int):
    """
    creates champion lists for each term in dictionary
    :param r: maximum length of champion list
    :return: champion lists for all terms
    """
    champion_lists: list[ChampionList] = []
    for ii in inverted_index_list:
        docs = list(sorted(ii.docs, key=lambda x: x[2]).__reversed__())
        champion_lists.append(ChampionList(ii.word, [x[0] for x in docs[:min(len(docs), r)]]))

    return champion_lists


def get_cluster(cluster_centers: list[list[float]], query_vector: list[float]):
    """
    find the cluster that is related to the query
    :param cluster_centers: list of cluster centers
    :param query_vector: vector of query
    :return: number of cluster; 0 for Heath, 1 for History, 2 for Mathematics 3 for Technology, 4 for Physics
    """
    res = 0
    s = get_similarity(cluster_centers[0], query_vector)
    for i in range(1, len(cluster_centers)):
        similarity = get_similarity(cluster_centers[i], query_vector)
        if similarity > s:
            s = similarity
            res = i

    return res


def calculate_query_vector_and_doc_vectors(q: str, inverted_index_list: list[InvertedIndex],
                                           champion_lists: list[ChampionList], doc_vectors: list[list[float]],
                                           cluster_centers: list[list[float]], docs: list[list]):
    """
    calculates query vector only due to idf of each term in query in dictionary
    also returns related docs vectors that appears in query terms from champion lists due to best cluster
    :return: query vector and query doc vectors
    """
    query_vector = [0.0] * len(inverted_index_list)
    query_doc_vectors = []

    # get vector of query
    words = q.split()
    stemmed_word = []
    for w in words:
        sw = stemming(w)
        if not sw == "":  # check if there is a non-empty string as stemmed word
            stemmed_word.append(sw)

            for i in range(len(inverted_index_list)):
                if inverted_index_list[i].word.__eq__(stemmed_word[-1]):
                    query_vector[i] = inverted_index_list[i].idf
                    break

    c = get_cluster(cluster_centers, query_vector)

    # filter docs due to related cluster to query
    for w in stemmed_word:
        for i in range(len(inverted_index_list)):
            if inverted_index_list[i].word.__eq__(w):
                for d in champion_lists[i].docs:
                    # check if query_doc_vectors contains this doc (d) or not
                    for qdv in query_doc_vectors:
                        if qdv[1] == d:
                            break
                    else:
                        if not c == 0:
                            if d - 1 in range(c * len(docs[c - 1]), c * len(docs[c - 1]) + len(docs[c])):
                                query_doc_vectors.append((doc_vectors[d - 1], d))
                        else:
                            if d - 1 in range(0, len(docs[0])):
                                query_doc_vectors.append((doc_vectors[d - 1], d))

    return query_vector, query_doc_vectors


def calculate_doc_vectors(inverted_index_list: list[InvertedIndex], docs_num: int):
    """
    calculates all doc vectors
    :return: a two dimensional array containing all doc vectors
    """
    doc_vectors: list[list[float]] = [[0.0 for _ in range(len(inverted_index_list))] for _ in range(docs_num)]

    for i in range(len(inverted_index_list)):
        for doc in inverted_index_list[i].docs:
            doc_vectors[doc[0] - 1][i] = doc[2]

    return doc_vectors


def calculate_cluster_centers(doc_vectors: list[list[float]], docs: list[list]):
    """
    calculates cluster centers
    :param docs: all docs (is used for get numbers of clusters and their docs)
    """
    cluster_centers = []

    for i in range(len(docs)):
        c = doc_vectors[i * len(docs[i])]
        for j in range(1, len(docs[i])):
            doc_no = i * len(docs[i]) + j
            for k in range(len(doc_vectors[doc_no])):
                c[k] = (c[k] + doc_vectors[doc_no][k]) / 2

        cluster_centers.append(c)

    return cluster_centers


def query(q: str, inverted_index_list: list[InvertedIndex], champion_lists: list[ChampionList],
          doc_vectors: list[list[float]], cluster_centers: list[list[float]], docs: list[list], k: int):
    """
    gets a query and prints related docs no
    :param q: the query
    """
    query_vector, query_doc_vectors = calculate_query_vector_and_doc_vectors(
        q, inverted_index_list, champion_lists, doc_vectors, cluster_centers, docs
    )

    result_arr = get_results(query_doc_vectors, query_vector, k)

    # printing results
    result_arr_len = len(result_arr)
    if result_arr_len == 0:
        print("چیزی پیدا نکردیم؛ لطفا کلمات جست‌وجوی خود را دقیق‌تر کنید یا کلمات بیش‌تری را به کار ببرید.")
    else:
        print("نتایج:")

        docs_arr = []
        for d in docs:
            docs_arr.extend(d)

        # printing name of docs
        for r in result_arr:
            print(docs_arr[r - 1][37:-4])


def heapify(arr, n, i):
    """
    to heapify subtree rooted at index i.
    :param arr: array we want to heapify
    :param n: is size of heap
    """
    largest = i  # initialize largest as root
    left = 2 * i + 1
    right = 2 * i + 2

    # see if left child of root exists and is greater than root
    if left < n and arr[i] < arr[left]:
        largest = left

    # see if right child of root exists and is greater than root
    if right < n and arr[largest] < arr[right]:
        largest = right

    # change root if needed
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # swap

        # heapify the root.
        heapify(arr, n, largest)


def heap_sort(arr):
    """
    main function to sort an array of given size
    :param arr: array we want to heapify
    """
    n = len(arr)

    # build a max-heap.
    # since last parent will be at ((n//2)-1) we can start at that location.
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # one by one extract elements
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # swap
        heapify(arr, i, 0)


def get_similarity(a: list[float], b: list[float]):
    """
    :return: similarity of two vectors a and b
    """
    numerator = 0

    sum_a2 = 0
    sum_b2 = 0

    # calculating numerator
    for i in range(len(a)):
        numerator += a[i] * b[i]

    if numerator == 0:
        return 0

    # calculating denominator
    for i in range(len(a)):
        sum_a2 += a[i] * a[i]
        sum_b2 += b[i] * b[i]

    denominator = sqrt(sum_a2) * sqrt(sum_b2)

    return numerator / denominator


def get_results(docs: list[(list[float], int)], q: list[float], k):
    """
    calculates similarities of vector of each doc with query vector and returns k best matches
    :param docs: vector of docs
    :param q: vector of query
    :return: array of k best match doc numbers
    """

    # creating similarity array
    similarity_arr = []
    for doc in docs:
        if not doc[1] in [x[1] for x in similarity_arr]:
            s = get_similarity(doc[0], q)
            if s != 0:
                similarity_arr.append((s, doc[1]))

    heap_sort(similarity_arr)

    return [x[1] for x in list(similarity_arr[-k:].__reversed__())]


def main():
    # constants
    r = 6  # maximum length of champion lists
    k = 5  # number of results

    # initializing inverted index
    inverted_index_list, docs_num, docs = create_inverted_index_list()
    inverted_index_list = sorted(inverted_index_list, key=lambda ii: ii.word)  # sort inverted index due to words
    champion_lists = create_champion_lists(inverted_index_list, r)  # calculating champion lists
    doc_vectors = calculate_doc_vectors(inverted_index_list, docs_num)  # calculating doc vectors
    cluster_centers = calculate_cluster_centers(doc_vectors, docs)  # calculating center od clusters

    # getting queries
    while True:
        q = input("\nعبارت مورد نظر خود برای جست‌وجو را وارد کنید (برای خروج ۰۰۰ (سه صفر) را وارد کیند):\n")
        if not q.__eq__("۰۰۰"):
            query(q, inverted_index_list, champion_lists, doc_vectors, cluster_centers, docs, k)
        else:
            return


if __name__ == '__main__':
    main()
