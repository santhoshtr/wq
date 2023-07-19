import functools
import os

from dotenv import load_dotenv
from llama_cpp import Llama

load_dotenv()

LLM_MODEL_PATH = os.environ.get("LLM_MODEL_PATH")


@functools.lru_cache
def get_llm():
    n_ctx = 2048  # Max context
    n_batch = 512  #  how many tokens are processed in parallel.
    model_path = LLM_MODEL_PATH
    return Llama(
        model_path=model_path,
        lora_path=None,
        n_batch=n_batch,
        n_ctx=n_ctx,
        n_gpu_layers=0,
        n_threads=max(len(os.sched_getaffinity(0)) - 2, 1),
        verbose=True,
    )


def llm_qa_streamer(question: str, context: str):
    prompt: str = f"""
Use the following pieces of context to answer the question. Answer should be short. If you don't know the answer, just say that you don't know, don't try to make up an answer.
Question: {question}
Context: {context}

Answer:
    """
    print(prompt)
    return llm_prompt_streamer(prompt)


def llm_prompt_streamer(prompt: str):
    stream = get_llm()(prompt, top_k=1, temperature=1, stream=True)
    for resp in stream:
        yield resp["choices"][0]["text"]
