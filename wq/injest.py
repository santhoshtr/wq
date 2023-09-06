import functools
import logging.config
import os

from dotenv import load_dotenv

from wq.embedding import *
from wq.vectorstore import *
from wq.wiki import Article

load_dotenv()

logging.config.fileConfig("logging.conf")


@functools.lru_cache
def get_vector_store():
    store_cls = eval(os.environ.get("VECTOR_STORE"))
    embedding_function = eval(os.environ.get("EMBEDDING_FUNCTION"))()
    vector_store = store_cls(embedding_function=embedding_function)
    return vector_store


def injest(language: str = "en", titles: list[str] = []):
    vector_store = get_vector_store()
    articles = [Article(language=language, title=title) for title in titles]
    vector_store.add_articles(articles)
    vector_store.persist()
    vector_store = None


if __name__ == "__main__":
    import fileinput
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="wikiembedder", description="Create embedding for given wikipedia articles")
    parser.add_argument("-l", "--language", default="en")
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="Files to read, if empty, stdin is used",
    )
    args = parser.parse_args()
    titles = []
    for title in fileinput.input(files=args.files):
        titles.append(title.strip())
    injest(language=args.language, titles=titles)
