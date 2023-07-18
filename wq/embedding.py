import csv
import functools
import logging
from hashlib import shake_256

import faiss
import numpy as np
from gpt4all import GPT4All

from api import wiki

logging.basicConfig(level=logging.INFO)

class WikiEmbedder(GPT4All):
    def __init__(
        self,
        model_name: str,
        model_path: str | None = None,
        model_type: str | None = None,
        allow_download: bool = True,
        n_threads: int | None = None,
    ):
        super().__init__(model_name, model_path, model_type, allow_download, n_threads)
        self.index = None
        self.sections = {}

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding.

        Args:
            text: The text document to generate an embedding for.

        Returns:
            An embedding of your document of text.
        """
        return self.model.generate_embedding(text)

    def get_article_text(self, language, title) -> list[str]:
        logging.info(f"[Wiki] {language}:{title}")
        wiki_text = wiki.get_page_text(language, title)
        if not wiki_text:
            raise Exception(f"Page does not exist? {language} - {title}")
            return []
        sections = wiki_text.split("\n")
        return sections

    def _id(self, *argv):
        return int(shake_256("".join(argv).encode()).hexdigest(6), 16)

    def add_article_embedding(self, language, title):
        sections = self.get_article_text(language, title)
        embedding_vectors = []
        ids = []
        for section_text in sections:
            if not section_text or len(section_text.strip()) < 2:
                continue
            embed_vector = self.embed_text(section_text)
            if not self.index:
                self.index = faiss.IndexFlatL2(len(embed_vector))
                # Pass the index to IndexIDMap
                self.index = faiss.IndexIDMap(self.index)
            section_id = self._id(language, title, section_text)
            ids.append(section_id)
            self.sections[section_id] = {
                "language": language,
                "title": title,
                "text": section_text,
            }

            embedding_vectors.append(embed_vector)

        vectors = np.array(embedding_vectors, dtype=np.float32)
        faiss.normalize_L2(vectors)
        self.index.add_with_ids(vectors, ids)

    def search(self, query, number_of_results=1):
        results = []
        query_vector = np.array([self.embed_text(query)], dtype=np.float32)
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(
            query_vector,
            k=number_of_results
        )
        for d in range(0, number_of_results):
            doc = self.docs[str(indices[0][d])]
            results.append({
                "query": query,
                "score": distances[0][d].astype(float),
                "context": doc.get("text"),
                "language": doc.get("language"),
                "title": doc.get("title"),
            })
        return results

    def save(self, file_path):
        faiss.write_index(self.index, file_path)
        with open(f"{file_path.split('.')[0]}.tsv", "w") as txt_file:
            txt_file.write(
                    "\t".join(["id", "language", "title", "text"])+"\n"
                )
            for section_id in self.sections:
                section = self.sections[section_id]
                txt_file.write(
                    "\t".join([str(section_id), section.get("language"), section.get("title"), section.get("text")])+"\n"
                )
            txt_file.close()

    def load(self, index_file_path):
        logging.info(f"Loading index from {index_file_path}")
        self.index = faiss.read_index(index_file_path)
        docs_dict = {}
        with open(f"{index_file_path.split('.')[0]}.tsv", "r") as docstore:
            docs = csv.DictReader(docstore, delimiter='\t')
            docs_dict = {}
            for doc in docs:
                docs_dict[doc['id']] = doc
        self.docs = docs_dict
        logging.info("Loaded index of type %s and size %d", type(self.index), self.index.ntotal)


@functools.lru_cache
def get_embedder() -> str:
    embedder = WikiEmbedder(model_name="ggml-all-MiniLM-L6-v2-f16.bin", model_path="./models")
    embedder.load("en-wiki.faiss")
    return embedder


# Run as:
# cat titles.txt | python -m wq.embedding
if __name__ == "__main__":
    import fileinput
    from argparse import ArgumentParser
    from tqdm import tqdm

    parser = ArgumentParser(prog="wikiembedder", description="Create embedding for given wikipedia article")
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="Files to read, if empty, stdin is used",
    )
    args = parser.parse_args()

    embedder = WikiEmbedder(model_name="ggml-all-MiniLM-L6-v2-f16.bin", model_path="./models")
    total_titles = len(args.files)
    pbar = tqdm(total=total_titles, desc="Embedding Progress", unit="article")
    for title in fileinput.input(files=args.files):
        embedder.add_article_embedding("en", title.strip())
        embedder.save("en-wiki.faiss")
        pbar.update(1)

    embedder.save("en-wiki.faiss")
    pbar.close()
