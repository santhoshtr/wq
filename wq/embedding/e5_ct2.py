import os
from typing import List
import ctranslate2
import numpy as np
import numpy.typing as npt
from dotenv import load_dotenv
from tokenizers import Tokenizer

load_dotenv()

# Text Embeddings by Weakly-Supervised Contrastive Pre-training https://arxiv.org/abs/2212.03533
# E5 is short for EmbEddings from bidirEctional Encoder rEpresentations
# [..] This model is initialized from xlm-roberta-base and continually trained on a mixture of multilingual
# datasets. It supports 100 languages from xlm-roberta, but low-resource languages
# may see performance degradation._

class E5CT2Embedder:
    def __init__(self):
        self.model = None
        self.model_name = os.environ.get("E5_MODEL_NAME")
        self.model_path = os.environ.get("MODEL_PATH")
        self.init()

    def init(self):
        self.tokenizer = Tokenizer.from_file(os.path.join(self.model_path, self.model_name, "tokenizer.json"))
        # max_seq_length = 256, for some reason sentence-transformers uses 256 even though the HF config has a max length of 128
        # https://github.com/UKPLab/sentence-transformers/blob/3e1929fddef16df94f8bc6e3b10598a98f46e62d/docs/_static/html/models_en_sentence_embeddings.html#LL480
        self.tokenizer.enable_truncation(max_length=128)
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=128)
        self.encoder = ctranslate2.Encoder(os.path.join(self.model_path, self.model_name), device="cpu")

    # Use pytorches default epsilon for division by zero
    # https://pytorch.org/docs/stable/generated/torch.nn.functional.normalize.html
    def _normalize(self, v: npt.NDArray) -> npt.NDArray:
        norm = np.linalg.norm(v, axis=1)
        norm[norm == 0] = 1e-12
        return v / norm[:, np.newaxis]

    def _forward(self, documents: List[str], batch_size: int = 32) -> npt.NDArray:
        all_embeddings = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            encoded = [self.tokenizer.encode(d) for d in batch]
            tokens = np.array([e.tokens for e in encoded])
            attention_mask = np.array([e.attention_mask for e in encoded])
            model_output = self.encoder.forward_batch(tokens)
            last_hidden_state = model_output.last_hidden_state
            # Perform mean pooling with attention weighting
            input_mask_expanded = np.broadcast_to(np.expand_dims(attention_mask, -1), last_hidden_state.shape)
            embeddings = np.sum(last_hidden_state * input_mask_expanded, 1) / np.clip(
                input_mask_expanded.sum(1), a_min=1e-9, a_max=None
            )
            embeddings = self._normalize(embeddings).astype(np.float32)
            all_embeddings.append(embeddings)
        return np.concatenate(all_embeddings)

    def __call__(self, texts: List[str]) -> list[float]:
        """
        Generate an embedding.

        Args:
            text: The text document to generate an embedding for.

        Returns:
            An embedding of your document of text.
        """
        return self._forward(texts).tolist()


messages = [
    "how much protein should a female eat",
    "summit define",
    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.",
    "Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top of a mountain. : 2  the highest level. : 3  a meeting or series of meetings between the leaders of two or more governments.",
]

if __name__ == "__main__":
    embedder = E5CT2Embedder()
    encoding_matrix = embedder(messages)
    print(np.inner(encoding_matrix, encoding_matrix))
