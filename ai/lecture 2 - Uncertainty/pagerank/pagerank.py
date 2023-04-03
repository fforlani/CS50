import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    links = corpus[page]
    if page in links:
        raise RuntimeError("Unexpected behavior: page should not link to itself, not ")
    if len(links) == 0:
        return {_page: 1 / len(corpus) for _page in corpus.keys()}
    model = {_page: (1 - damping_factor) / len(corpus) for _page in corpus.keys()}
    for link in links:
        model[link] += damping_factor / len(links)
    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageRank = {page : 0 for page in corpus.keys()}
    currentPage = list(corpus)[random.randint(0, len(corpus)-1)]
    pageRank[currentPage] += 1
    models = {page: transition_model(corpus, page, damping_factor) for page in corpus.keys()}
    for i in range(1, n):  # starting at 1 beacuse I already chose the first page
        currentPage = random.choices(list(models[currentPage].keys()), weights=list(models[currentPage].values()))[0]
        pageRank[currentPage] += 1
    pageRank.update((page, occurrences/n) for page, occurrences in pageRank.items())
    return pageRank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    goal = 0.001
    accuracy = 1 # it is important that at start it is greater than goal
    pageNum = len(corpus)
    pageRank = {page: 1/pageNum for page in corpus.keys()}
    while accuracy > goal:
        accuracy = 0
        for page in corpus:
            newRank = (1-damping_factor)/pageNum + \
                             damping_factor*sum([pageRank[previousPage]/len(links) for previousPage, links in corpus.items() if page in corpus[previousPage]])
            accuracy = max(abs(newRank - pageRank[page]), accuracy)
            pageRank[page] = newRank
    pageRank = {page: rank / sum(pageRank.values()) for page, rank in pageRank.items()} # needed to normalize the sum rank (sum = 1)
    return pageRank


if __name__ == "__main__":
    main()
