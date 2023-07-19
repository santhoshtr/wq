from typing import Any

from wq import Article


class BaseVectorStore:
    def __init__(self, embedding_function=None) -> None:
        self.embedding_function = embedding_function

    def embed(self, texts: list[str]) -> list[list[Any]]:
        if not self.embedding_function:
            raise Exception("No embedding_function defined")
        return self.embedding_function(texts)

    def query(self, query):
        raise Exception("Not implemented")

    def add_articles(self, articles: list[Article]):
        raise Exception("Not implemented")

    def add_article(self, article: Article):
        raise Exception("Not implemented")
