from typing import List

from pydantic import BaseModel


class RetrievalResult(BaseModel):
    id: str
    title: str
    wikicode: str
    content_html: str
    score: float
    revision: int


class ArticleSection(BaseModel):
    section: str
    sentences: List[str]
