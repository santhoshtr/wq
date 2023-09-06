"""Chroma is the open-source embedding database."""

import logging
import logging.config
import os
from typing import List

import numpy as np
import redis
from dotenv import load_dotenv
from redis.commands.search.field import NumericField, TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query as RediSearchQuery

from wq.types import ArticleSection, RetrievalResult
from wq.vectorstore import BaseVectorStore
from wq.wiki import Article

load_dotenv()


logging.config.fileConfig("logging.conf")

# Read environment variables for Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
VECTOR_DIM = 384  # length of the vectors
VECTOR_NUMBER = 100  # initial number of vectors
INDEX_NAME = "wiki-embeddings-index"  # name of the search index

DISTANCE_METRIC = "COSINE"  # distance metric for the vectors (ex. COSINE, IP, L2)


class RedisStore(BaseVectorStore):
    def __init__(self, embedding_function=None, threshold_score=0.87):
        super().__init__(embedding_function, threshold_score)
        self.db = self.connect()

    def connect(self):
        articles_schema = [
            TextField("$.title", as_name="title"),
            NumericField("$.revision", as_name="revision"),
            TextField("$.wikicode", as_name="wikicode"),
            TextField("$.section", as_name="section"),
        ]
        vector_schema = [
            TextField("$.sentence", as_name="sentence"),
            TextField("$.section_key", as_name="section_key"),
            VectorField(
                "$.sentence_vector",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": VECTOR_DIM,
                    "DISTANCE_METRIC": DISTANCE_METRIC,
                    "INITIAL_CAP": VECTOR_NUMBER,
                },
                as_name="sentence_vector",
            ),
        ]
        # Connect to Redis
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        redis_client.ping()

        try:
            redis_client.ft("wiki-sections").info()
            redis_client.ft("sentence-embedding").info()
            # redis_client.ft(INDEX_NAME).dropindex()
            logging.debug("Index already exists")
        except Exception:
            # Create RediSearch Index
            redis_client.ft("wiki-sections").create_index(
                articles_schema, definition=IndexDefinition(prefix=["w"], index_type=IndexType.JSON)
            )
            redis_client.ft("sentence-embedding").create_index(
                vector_schema, definition=IndexDefinition(prefix=["s"], index_type=IndexType.JSON)
            )

        return redis_client

    def add_article(self, article: Article) -> None:
        try:
            sections: List[ArticleSection] = article.get_sections()
        except Exception:
            logging.exception("message")
            return

        existing_revision = self.db.keys(f"w:{article.language}:{article.title}:{article.revision}*")
        if len(existing_revision):
            # Article with same revision already exist.
            logging.warn(f"{article.language}:{article.title} with revision {article.revision} already exist")
            # return

        existing_keys = self.db.keys(f"w:{article.language}:{article.title}*")
        if len(existing_keys):
            # Remove existing records
            self.db.delete(*existing_keys)
            sentences = self.db.keys(f"s:w:{article.language}:{article.title}*")
            self.db.delete(*sentences)

        pipeline = self.db.pipeline()

        section: ArticleSection
        index: int
        for index, section in enumerate(sections):
            doc = {}
            section_key = f"w:{article.language}:{article.title}:{article.revision}:{index}"
            doc["section"] = section.section
            doc["title"] = article.title
            doc["wikicode"] = article.language
            doc["revision"] = article.revision

            pipeline.json().set(section_key, "$", doc)

            sentence_vectors = self.embed(section.sentences)

            sentence: str
            sindex: int
            for sindex, sentence in enumerate(section.sentences):
                sentence_key = f"s:{section_key}:{sindex}"
                sentence_doc = {}
                sentence_doc["sentence"] = sentence
                sentence_doc["section_key"] = section_key
                sentence_doc["sentence_vector"] = sentence_vectors[sindex]
                pipeline.json().set(sentence_key, "$", sentence_doc)

            pipeline.execute()

    def query(self, query: str, n_results=1) -> list[RetrievalResult]:

        k = n_results
        # Creates embedding vector from user query
        embedded_query = self.get_query_embedding(query)

        # Prepare the Query
        base_query = f"(*)=>[KNN {k} @sentence_vector $query_vector as vector_score]"
        query = (
            RediSearchQuery(base_query)
            .return_fields("sentence", "section_key", "vector_score")
            .sort_by("vector_score")
            .paging(0, k)
            .dialect(2)
        )

        params_dict = {"query_vector": np.array(embedded_query).astype(dtype=np.float32).tobytes()}
        # perform vector search
        sentence_results = self.db.ft("sentence-embedding").search(query, query_params=params_dict)

        search_results = []
        for _i, doc in enumerate(sentence_results.docs):
            score = 1 - float(doc.vector_score)
            score = self.normalized_score(score)
            if score < self.threshold_score:
                continue
            section_doc = self.db.json().get(doc.section_key)
            print(score, doc.sentence)
            search_results.append(
                RetrievalResult(
                    id=doc.id,
                    title=section_doc.get("title"),
                    revision=int(section_doc.get("revision")),
                    wikicode=section_doc.get("wikicode"),
                    content_html=section_doc.get("section"),
                    score=score,
                )
            )
        return search_results

    def normalized_score(self, score: float) -> float:
        return round(score, 3)
