from typing import Any

from tqdm import tqdm

from wq.types import RetrievalResult
from wq.wiki import Article


class BaseVectorStore:
    def __init__(self, embedding_function=None, threshold_score=0.85) -> None:
        self.embedding_function = embedding_function
        self.threshold_score = threshold_score

    def embed(self, texts: list[str]) -> list[list[Any]]:
        if not self.embedding_function:
            raise Exception("No embedding_function defined")
        return self.embedding_function(texts)

    def get_query_embedding(self, query):
        return self.embed([query])[0]

    def query(self, query) -> list[RetrievalResult]:
        raise Exception("Not implemented")

    def add_article(self, article: Article):
        raise Exception("Not implemented")

    def persist(self):
        pass

    def add_articles(self, articles: list[Article]):
        pbar = tqdm(total=len(articles))
        for article in articles:
            pbar.set_description(f"Processing {article.title}")
            self.add_article(article)
            pbar.update(1)
        pbar.close()

    def normalized_score(self, score: float) -> float:
        return score
