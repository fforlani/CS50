import nltk
import sys
import os
import string
import re
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    while (True):
        # Prompt user for query
        query = set(tokenize(input("Query: ")))

        # Determine top file matches according to TF-IDF
        filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

        # Extract sentences from top files
        sentences = dict()
        for filename in filenames:
            for passage in files[filename].split("\n"):
                for sentence in nltk.sent_tokenize(passage):
                    tokens = tokenize(sentence)
                    if tokens:
                        sentences[sentence] = tokens

        # Compute IDF values across sentences
        idfs = compute_idfs(sentences)

        # Determine top sentence matches
        matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
        for match in matches:
            print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    return {file[:-4]: open("corpus" + os.sep + file, encoding="utf8").read() for file in os.listdir(directory) if file.endswith(".txt")}


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    document = document.lower()
    document = re.sub("[" + string.punctuation + "]", "", document)
    words = [word for word in document.split(" ") if word not in nltk.corpus.stopwords.words("english")]
    return nltk.word_tokenize(" ".join(words))


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    num_doc_per_word = {}
    for words in documents.values():
        for word in set(words):
            if word in num_doc_per_word.keys():
                num_doc_per_word[word] += 1
            else:
                num_doc_per_word[word] = 1
    num_doc = len(documents)
    return {word: math.log(num_doc/num) for word, num in num_doc_per_word.items()}


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idf = {file: 0 for file in files}
    for file in files.keys():
        for word in set(files[file]):
            if word in query:
                tf_idf[file] += files[file].count(word) * idfs[word]
    return [file for file, _ in sorted(tf_idf.items(), key=lambda item: -item[1])][:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_score = {sentence: 0 for sentence in sentences.keys()}
    for word in query:
        for sentence, words in sentences.items():
            if word in words:
                sentence_score[sentence] += idfs[word]

    # defining top sentences to return managing also ranking ties
    top_sent = []
    ordered = sorted(sentence_score.items(), key=lambda item: -item[1])
    for i in range(n):
        if ordered[0][1] == ordered[1][1]:
            top_sent.append(ordered[0][0] if query_term_density(query, sentences[ordered[0][0]]) >= query_term_density(query, sentences[ordered[1][0]])
                            else ordered[1][0])
        else:
            top_sent.append(ordered[0][0])
        ordered = ordered[1:]
    return top_sent


def query_term_density(query, sentence):
    """
    Calculating query term density as the ratio between term that appears both in query and sentence and sentence lenght
    """
    count = 0
    for word in query:
        if word in sentence:
            count += 1
    return count/len(sentence)


if __name__ == "__main__":
    main()
