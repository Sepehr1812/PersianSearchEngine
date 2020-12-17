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


def main():
    # constants
    docs_num = 10

    inverted_index_list = create_inverted_index_list(docs_num)
    inverted_index_list = remove_over_repeated_words(inverted_index_list, docs_num)


if __name__ == '__main__':
    main()
