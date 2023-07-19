"""Chroma is the open-source embedding database."""

import os

import chromadb
from dotenv import load_dotenv
from tqdm import tqdm

from wq import Article
from wq.vectorstore import BaseVectorStore

load_dotenv()


persist_directory = os.environ.get("VECTOR_STORE_DEST")

CHROMA_SETTINGS = chromadb.config.Settings(anonymized_telemetry=False)


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, embedding_function=None):
        super().__init__(embedding_function)
        self.db = chromadb.PersistentClient(path=persist_directory, settings=CHROMA_SETTINGS)
        self.collection = self.db.get_or_create_collection(name="wiki_collection")

    def add_article(self, article):
        documents = []
        metadatas = []
        ids = set()

        article_metadata = article.get_page_metadata()
        if "title" not in self.metadata:
            # Article not found?
            return
        text_sections, html_sections = article.get_sections()
        for index, section in enumerate(text_sections):
            section_id = str(article._id(article.language, article.title, section))
            if section_id in ids:
                continue
            documents.append(section)
            metadata = article_metadata.copy()
            metadata["html"] = html_sections[index]
            metadatas.append(metadata)
            ids.add(section_id)

        self.collection.upsert(documents=documents, metadatas=metadatas, ids=list(ids))

    def add_articles(self, articles: list[Article]):
        pbar = tqdm(total=len(articles))
        for article in articles:
            pbar.set_description(f"Processing {article.title}")
            self.add_article(article)
            pbar.update(1)
        pbar.close()

    def persist(self):
        # Chroma >= 0.4.0 saves all writes to disk instantly and
        # so persist is no longer needed.
        pass

    def query(self, query, n_results=1):
        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )
