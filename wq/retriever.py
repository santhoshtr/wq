import functools
import os

from dotenv import load_dotenv

from wq.embedding import *
from wq.vectorstore import *

load_dotenv()


@functools.lru_cache
def get_vector_store():
    store_cls = eval(os.environ.get("VECTOR_STORE"))
    embedding_function = eval(os.environ.get("EMBEDDING_FUNCTION"))()
    vector_store = store_cls(embedding_function=embedding_function)
    return vector_store


def retrieve(query: str, n_results=2):
    # embedding_function = SBERTEmbedder()
    # vector_store = ChromaVectorStore(embedding_function=embedding_function)
    vector_store = get_vector_store()
    retrieval_results: list[RetrievalResult] = vector_store.query(query=query, n_results=n_results)
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
