""" This project is implementation of a search engine with Information Retrieval principles """
import re
from typing import List


class InvertedIndex:
    """
    Inverted Index class that contains a word and list of docs that include that word
    """

    def __init__(self, word: str, first_doc: int):
        self.word: str = word
        self.docs: List[int] = [first_doc]


def create_inverted_index_list(doc_num: int):
    """
    creates an inverted index list from docs in sampleDocs folder
    :param doc_num: number of docs
    :return: inverted index list
    """
    inverted_index_list: List[InvertedIndex] = []

    for i in range(1, doc_num + 1):
        with open("sampleDocs/" + str(i) + ".txt", "r", encoding='utf-8') as f:
            sentences = [re.split("\\s+", line.rstrip('\n')) for line in f]
            for sentence in sentences:
                for word in sentence:
                    for ii in inverted_index_list:
                        if ii.word == word and not ii.docs.__contains__(i):
                            ii.docs.append(i)
                            break
                    else:
                        inverted_index_list.append(InvertedIndex(word, i))

    return inverted_index_list


def main():
    # constants
    docs_num = 10

    inverted_index_list = create_inverted_index_list(docs_num)


if __name__ == '__main__':
    main()
