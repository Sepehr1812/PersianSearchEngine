""" This project is implementation of a search engine with Information Retrieval principles on some Persian docs """
import re
from typing import List


class InvertedIndex:
    """
    Inverted Index class that contains a word and list of docs that include that word
    """

    def __init__(self, word: str, first_doc: int):
        self.word: str = word
        self.docs: List[int] = [first_doc]


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
                                if not ii.docs.__contains__(i):
                                    ii.docs.append(i)
                                break
                        else:
                            inverted_index_list.append(InvertedIndex(stemmed_word, i))

    return inverted_index_list


def remove_over_repeated_words(inverted_index_list: List[InvertedIndex], docs_num: int):
    """
    removed all words that there are in more than %70 of all docs and their lengths are less than 4
    :param docs_num: number of all docs
    :return: filtered inverted index
    """
    return list(filter(lambda ii: len(ii.docs) < docs_num * 0.7 or len(ii.word) >= 5, inverted_index_list))


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


def main():
    # constants
    docs_num = 10

    # initializing inverted index
    inverted_index_list = create_inverted_index_list(docs_num)
    inverted_index_list = remove_over_repeated_words(inverted_index_list, docs_num)
    inverted_index_list = sorted(inverted_index_list, key=lambda ii: ii.word)  # sort inverted index due to words

    # getting queries
    while True:
        q = input("\nعبارت مورد نظر خود برای جست‌وجو را وارد کنید (برای خروج ۰۰۰ (سه صفر) را وارد کیند):\n")
        if not q.__eq__("۰۰۰"):
            query(q, inverted_index_list, docs_num)
        else:
            return


if __name__ == '__main__':
    main()
