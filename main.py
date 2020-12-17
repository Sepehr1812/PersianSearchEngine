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
    result = result.replace("خواهم", "")
    result = result.replace("خواهی", "")
    result = result.replace("خواهد", "")
    result = result.replace("خواهیم", "")
    result = result.replace("خواهید", "")
    result = result.replace("خواهند", "")
    result = result.replace("بودم", "")
    result = result.replace("بودی", "")
    result = result.replace("بود", "")
    result = result.replace("بودیم", "")
    result = result.replace("بودید", "")
    result = result.replace("بودند", "")
    result = result.replace("باشم", "")
    result = result.replace("باشی", "")
    result = result.replace("باشد", "")
    result = result.replace("باشیم", "")
    result = result.replace("باشید", "")
    result = result.replace("باشند", "")

    result = result.removesuffix('ها')  # remove plural sign ها

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
        with open("sampleDocs/" + str(i) + ".txt", "r", encoding='utf-8') as f:
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


def main():
    # constants
    docs_num = 10

    inverted_index_list = create_inverted_index_list(docs_num)


if __name__ == '__main__':
    main()
