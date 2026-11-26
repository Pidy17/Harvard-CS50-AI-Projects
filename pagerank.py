
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

    print("PageRank Results from Iteration")

    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a set of all other pages in the corpus that are linked to by the page.
    """

    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):

        if not filename.endswith(".html"):
            continue

        with open(os.path.join(directory, filename)) as f:
            contents = f.read()

            links = re.findall(
                r'<a\s+(?:[^>]*?)href="([^"]*)"',
                contents
            )

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
    Return a probability distribution over which page to visit next.
    """

    total_pages = len(corpus)

    probabilities = {}

    links = corpus[page]

    # If the page has no outgoing links, treat it as linking
    # to every page in the corpus.
    if not links:
        links = set(corpus.keys())

    # Calculate the probability for each page.
    for destination in corpus:

        # Random jump probability.
        probabilities[destination] = (1 - damping_factor) / total_pages

        # Link-following probability.
        if destination in links:
            probabilities[destination] += damping_factor / len(links)

    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling.
    """

    pages = list(corpus.keys())

    # Count visits to each page.
    visits = {page: 0 for page in pages}

    # Choose the first page randomly.
    current_page = random.choice(pages)

    # Generate n samples.
    for _ in range(n):

        # Record the current page.
        visits[current_page] += 1

        # Generate the next page using the transition model.
        probabilities = transition_model(
            corpus,
            current_page,
            damping_factor
        )

        current_page = random.choices(
            list(probabilities.keys()),
            weights=list(probabilities.values()),
            k=1
        )[0]

    # Convert visit counts into PageRank probabilities.
    ranks = {}

    for page in pages:
        ranks[page] = visits[page] / n

    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteration.
    """

    total_pages = len(corpus)

    # Initially assign every page an equal PageRank.
    ranks = {
        page: 1 / total_pages
        for page in corpus
    }

    # Continue until all PageRank values converge.
    while True:

        new_ranks = {}

        for page in corpus:

            # Random jump contribution.
            rank = (1 - damping_factor) / total_pages

            # Contributions from pages linking to this page.
            for other_page in corpus:

                links = corpus[other_page]

                # A page with no links links to every page.
                if not links:
                    links = set(corpus.keys())

                if page in links:
                    rank += (
                        damping_factor
                        * ranks[other_page]
                        / len(links)
                    )

            new_ranks[page] = rank

        # Check whether all PageRank values have converged.
        converged = True

        for page in corpus:

            if abs(new_ranks[page] - ranks[page]) > 0.001:
                converged = False
                break

        ranks = new_ranks

        if converged:
            break

    return ranks


if __name__ == "__main__":
    main()