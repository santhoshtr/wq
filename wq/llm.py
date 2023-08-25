import functools
import os

from dotenv import load_dotenv
from llama_cpp import Llama

load_dotenv()

LLM_MODEL_PATH = os.environ.get("LLM_MODEL_PATH")


@functools.lru_cache
def get_llm():
    model_path = LLM_MODEL_PATH
    return Llama(
        model_path=model_path,
        # lora_path=None,
        # n_batch=n_batch,
        # n_ctx=n_ctx,
        n_threads=max(len(os.sched_getaffinity(0)) - 1, 1),
        verbose=True,
    )


def llm_qa_hyde(question: str) -> str:
    instruction = (
        "Answer this question as if knows everything. If you do not know the answer, make up a hypothetical answer."
    )

    prompt = f"### Instruction\n{instruction}\nQuestions:{question}\n\n### Response\n"
    llm = get_llm()
    print(prompt)
    response = llm(prompt, top_k=1, temperature=1, stream=False)
    return response["choices"][0]["text"]


def llm_qa_streamer(question: str, context: str):
    instruction = "Use the following pieces of context to answer the question. Answer should be short. If you don't know the answer, just say that you don't know, don't try to make up an answer."
    prompt = f"### Instruction\n{instruction}\n\nQuestion: {question}\nContext:\n\n {context}\n\n### Response\n"
    print(prompt)
    return llm_prompt_streamer(prompt)


def llm_prompt_streamer(prompt: str):
    llm = get_llm()
    stream = llm(prompt, top_k=1, temperature=1, stream=True)
    for resp in stream:
        yield resp["choices"][0]["text"]

    llm = None
