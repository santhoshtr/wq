import logging

from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)


class SBERTEmbedder:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        model_path: str | None = None,
        model_type: str | None = None,
        allow_download: bool = True,
        n_threads: int | None = None,
    ):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.sections = {}

    def __call__(self, text: str) -> list[float]:
        """
        Generate an embedding.

        Args:
            text: The text document to generate an embedding for.

        Returns:
            An embedding of your document of text.
        """
        return self.model.encode(text)
