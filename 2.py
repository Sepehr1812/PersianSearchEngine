""" This project is implementation of a search engine with Information Retrieval principles on some Persian docs """
import re
from math import sqrt, log10
from typing import List


class InvertedIndex:
    """
    Inverted Index class that contains a word and list of docs that include that word
    """

    def __init__(self, word: str, first_doc: int):
        self.word: str = word
        self.docs: list[(int, int, float)] = [(first_doc, 1, 0)]  # the second argument is tf, the third one is weight
        self.idf: float = 0.0

    def calculate_weights(self):
        """
        calculates weights of term self.word in different docs
        """
        for i in range(len(self.docs)):
            doc = self.docs[i]
            self.docs[i] = (doc[0], doc[1], (1 + log10(doc[1])) * log10(self.idf))


class ChampionList:
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


def create_inverted_index_list(doc_num: int):
    """
    creates an inverted index list from docs in SampleDocs folder
    :param doc_num: number of docs
    :return: inverted index list
    """
    inverted_index_list: List[InvertedIndex] = []

    for i in range(1, doc_num + 1):
        with open("SampleDocs/" + str(i) + ".txt", "r", encoding='utf-8') as f:
            sentences = [re.split("\\s+", line.rstrip('\n')) for line in f]
            for sentence in sentences:
                for word in sentence:
                    stemmed_word = stemming(word)
                    if not stemmed_word == "":  # check if there is a non-empty string as stemmed word
                        for ii in inverted_index_list:
                            if ii.word.__eq__(stemmed_word):
                                if not [x[0] for x in ii.docs].__contains__(i):
                                    ii.docs.append((i, 1))
                                else:
                                    # increasing tf
                                    for j in range(len(ii.docs)):
                                        if ii.docs[j][0] == i:
                                            ii.docs[j] = (i, ii.docs[j][1] + 1)
                                            break
                                break
                        else:
                            inverted_index_list.append(InvertedIndex(stemmed_word, i))

    # calculating idf and weights
    for ii in inverted_index_list:
        ii.idf = doc_num / len(ii.docs)
        ii.calculate_weights()

    return inverted_index_list


def remove_over_repeated_words(inverted_index_list: List[InvertedIndex], docs_num: int):
    """
    removed all words that there are in more than %70 of all docs and their lengths are less than 4
    :param docs_num: number of all docs
    :return: filtered inverted index
    """
    return list(filter(lambda ii: len(ii.docs) < docs_num * 0.7 or len(ii.word) >= 5, inverted_index_list))


def create_champion_lists(inverted_index_list: list[InvertedIndex], r: int):
    champion_lists: list[ChampionList] = []
    for ii in inverted_index_list:
        docs = list(sorted(ii.docs, key=lambda x: x[2]).__reversed__())
        champion_lists.append(ChampionList(ii.word, [x[0] for x in docs[:min(len(docs), r)]]))

    return champion_lists


def query(q: str, inverted_index_list: List[InvertedIndex], docs_num: int):
    """
    gets a query and prints related docs no
    :param q: the query
    :param docs_num: number of all docs
    """
    result_arr = []

    words = q.split()
    for w in words:
        sw = stemming(w)
        for ii in inverted_index_list:
            if ii.word.__eq__(sw):
                result_arr.append(ii.docs)
                break

    # printing results
    result_arr_len = len(result_arr)
    if result_arr_len == 0:
        print("چیزی پیدا نکردیم؛ لطفا کلمات جست‌وجوی خود را دقیق‌تر کنید یا کلمات بیش‌تری را به کار ببرید.")
    elif result_arr_len == 1:
        print("نتایج:")
        for r in result_arr[0]:
            print(r)
    else:
        # sorting best results
        occurrence_arr = [0] * docs_num
        for r in result_arr:
            for doc_no in r:
                occurrence_arr[doc_no - 1] += 1

        # printing results
        print("نتایج:")
        i = len(words)
        while i > 0:
            for j in range(len(occurrence_arr)):
                if occurrence_arr[j] == i:
                    print(j + 1)
            i -= 1


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


def get_results(docs: list[list[float]], q: list[float], k):
    """
    calculates similarities of vector of each doc with query vector and returns k best matches
    :param docs: vector of docs
    :param q: vector of query
    :return: array of k best match doc numbers
    """

    # creating similarity array
    similarity_arr = []
    for i in range(len(docs)):
        s = get_similarity(docs[i], q)
        if s != 0:
            similarity_arr.append((s, i + 1))

    heap_sort(similarity_arr)

    return list(similarity_arr[-k].__reversed__())


def main():
    # constants
    docs_num = 10

    # initializing inverted index
    inverted_index_list = create_inverted_index_list(docs_num)
    inverted_index_list = remove_over_repeated_words(inverted_index_list, docs_num)  # index elimination
    inverted_index_list = sorted(inverted_index_list, key=lambda ii: ii.word)  # sort inverted index due to words
    champion_lists = create_champion_lists(inverted_index_list, r=6)

    # getting queries
    while True:
        q = input("\nعبارت مورد نظر خود برای جست‌وجو را وارد کنید (برای خروج ۰۰۰ (سه صفر) را وارد کیند):\n")
        if not q.__eq__("۰۰۰"):
            query(q, inverted_index_list, docs_num)
        else:
            return


if __name__ == '__main__':
    main()
