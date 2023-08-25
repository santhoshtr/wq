"""Chroma is the open-source embedding database."""

import os

import numpy as np
import redis
from dotenv import load_dotenv
from redis.commands.search.field import NumericField, TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query as RediSearchQuery

from wq import Article
from wq.types import RetrievalResult
from wq.vectorstore import BaseVectorStore

load_dotenv()

# Read environment variables for Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
VECTOR_DIM = 384  # length of the vectors
VECTOR_NUMBER = 100  # initial number of vectors
INDEX_NAME = "wiki-embeddings-index"  # name of the search index
PREFIX = "wiki"  # prefix for the document keys
DISTANCE_METRIC = "COSINE"  # distance metric for the vectors (ex. COSINE, IP, L2)


class RedisStore(BaseVectorStore):
    def __init__(self, embedding_function=None):
        super().__init__(embedding_function)
        self.db = self.connect()

    def connect(self):
        schema = [
            TextField("$.title", as_name="title"),
            NumericField("$.revision", as_name="revision"),
            TextField("$.wikicode", as_name="wikicode"),
            TextField("$.content_html", as_name="content_html"),
            VectorField(
                "$.content_vector",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": VECTOR_DIM,
                    "DISTANCE_METRIC": DISTANCE_METRIC,
                    "INITIAL_CAP": VECTOR_NUMBER,
                },
                as_name="content_vector",
            ),
        ]
        # Connect to Redis
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        redis_client.ping()

        try:
            redis_client.ft(INDEX_NAME).info()
            # redis_client.ft(INDEX_NAME).dropindex()
            print("Index already exists")
        except:
            # Create RediSearch Index
            redis_client.ft(INDEX_NAME).create_index(
                schema, definition=IndexDefinition(prefix=[PREFIX], index_type=IndexType.JSON)
            )
        return redis_client

    def add_article(self, article: Article):
        try:
            article_metadata = article.get_page_metadata()
            if "title" not in article_metadata:
                # Article not found?
                return

            text_sections, html_sections = article.get_sections()
        except:
            return

        content_vectors = self.embed(text_sections)

        # Remove existing records
        existing_keys = self.db.keys(f"{PREFIX}:{article.language}:{article.title}*")
        if len(existing_keys):
            self.db.delete(*existing_keys)

        pipeline = self.db.pipeline()
        revision = int(article_metadata.get("revision"))
        for index, html_section in enumerate(html_sections):
            doc = {}
            key = f"{article.language}:{article.title}:{revision}:{index}"
            doc["content_html"] = html_section
            doc["title"] = article.title
            doc["wikicode"] = article.language
            doc["revision"] = revision
            doc["content_vector"] = content_vectors[index]

            pipeline.json().set(f"{PREFIX}:{key}", "$", doc)

        pipeline.execute()

        print(f"Loaded {self.db.info()['db0']['keys']} documents in Redis search index with name: {INDEX_NAME}")

    def query(self, query, n_results=1):
        return_fields: list = ["title", "wikicode", "revision", "content_html", "vector_score"]

        k = n_results
        # Creates embedding vector from user query
        embedded_query = self.get_query_embedding(query)

        # Prepare the Query
        base_query = f"(*)=>[KNN {k} @content_vector $query_vector as vector_score]"
        query = (
            RediSearchQuery(base_query).return_fields(*return_fields).sort_by("vector_score").paging(0, k).dialect(2)
        )

        params_dict = {"query_vector": np.array(embedded_query).astype(dtype=np.float32).tobytes()}

        # perform vector search
        results = self.db.ft(INDEX_NAME).search(query, query_params=params_dict)
        print(results)
        search_results = []
        for _i, doc in enumerate(results.docs):
            score = 1 - float(doc.vector_score)
            search_results.append(
                RetrievalResult(
                    id=doc.id,
                    title=doc.title,
                    revision=int(doc.revision),
                    wikicode=doc.wikicode,
                    content_html=doc.content_html,
                    score=round(score, 3),
                )
            )
        return search_results
