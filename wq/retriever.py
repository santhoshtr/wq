import functools
import logging
import logging.config
import os

from dotenv import load_dotenv

from wq.embedding import *
from wq.injest import injest
from wq.types import RetrievalResult
from wq.vectorstore import *
from wq.wiki.api import search_wikipedia

load_dotenv()


logging.config.fileConfig("logging.conf")


@functools.lru_cache
def get_vector_store():
    store_cls = eval(os.environ.get("VECTOR_STORE"))
    embedding_function = eval(os.environ.get("EMBEDDING_FUNCTION"))()
    vector_store = store_cls(embedding_function=embedding_function)
    return vector_store


def retrieve(query: str, n_results=2, try_with_search_and_embedding=False):
    vector_store = get_vector_store()
    retrieval_results: list[RetrievalResult] = vector_store.query(query=query, n_results=n_results)
    if try_with_search_and_embedding and len(retrieval_results) == 0:
        # find relevant articles by using wikipedia search, index them and try again.
        titles = search_wikipedia(query, wikicode="en")
        logging.debug(f"Retrying: {titles}")
        injest("en", titles)
        retrieval_results = vector_store.query(query=query, n_results=n_results)

    return retrieval_results


if __name__ == "__main__":
    import fileinput
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="wikiembedder", description="Query embedding for given wikipedia articles")
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="Files to read, if empty, stdin is used",
    )
    args = parser.parse_args()
    for query in fileinput.input(files=args.files):
        print(retrieve(query, n_results=2))
