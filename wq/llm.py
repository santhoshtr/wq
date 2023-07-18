import functools
import os

from llama_cpp import Llama


@functools.lru_cache
def get_llm():
    n_ctx = 2048  # Max context
    n_batch = 512  #  how many tokens are processed in parallel.
    model_path = "./models/orca-mini-3b.ggmlv3.q4_0.bin"
    # model_path = "./models/llama-7b.ggmlv3.q4_1.bin"
    return Llama(
        model_path = model_path,
        lora_path = None,
        n_batch = n_batch,
        n_ctx = n_ctx,
        n_gpu_layers = 0,
        n_threads = max(len(os.sched_getaffinity(0)) - 2, 1),
        verbose = True
    )

def llm_qa_streamer(query: str, context:str):
    prompt:str =f"""
Answer the question only using the provided context. Answer should be short. If answer not found in the context, stop.
Question: {query}
Context: {context}
Answer:
    """
    print(prompt)
    return llm_prompt_streamer(prompt)

def llm_prompt_streamer(prompt: str):
    stream = get_llm()(
        prompt,
        top_k=1,
        temperature=1,
        stream=True
    )
    for resp in stream:
        yield resp["choices"][0]["text"]
