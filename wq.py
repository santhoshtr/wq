from api import chatgpt, wiki
from utils import find_entities, chunk, annotate
import json
import logging
import sys
import multiprocessing
from distillbertqa import onnx_qa
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import redis

cache = redis.Redis(host="localhost", port=6379)

MAX_WORKERS = multiprocessing.cpu_count()
THRESHOLD_SCORE = 0.9
logging.basicConfig(level=logging.INFO)
import redis

cache = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)


def get_questions(language, title: str):
    wiki_text = wiki.get_page_text(language, title, 10)
    if not wiki_text:
        logging.info(f"Page does not exist? {language} - {title}")
        return []
    logging.info(f"[ChatGPT] Getting questions for {language} - {title}...")
    responseStr = chatgpt.create_response(wiki_text)
    response = json.loads(responseStr)
    logging.info(f"[ChatGPT] Got questions for {language} - {title}")
    if "questions" in response:
        return response["questions"]
    elif isinstance(response, list) and "question" in response[0]:
        # Sometimes chatgpt gives array of objects without key
        return response
    else:
        logging.error("Unexpected response from chatgpt API")
        logging.debug(responseStr)


def qa_worker(question, language, title) -> List[Dict]:
    logging.info(f'[Wiki] {language}:{title} Searching for "{question}"')
    answers = []
    wiki_text = wiki.get_page_text(language, title)
    if not wiki_text:
        logging.info(f"Page does not exist? {language} - {title}")
        return []
    full_context = wiki_text.split("\n\n")
    context_chunks = list(chunk(full_context, 5))
    contexts = []
    for context_chunk in context_chunks:
        context = "\n".join(context_chunk)
        if not context or len(context.strip()) == 0:
            continue
        contexts.append(context)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures_context_map = {
            executor.submit(onnx_qa, question, context): context for context in contexts
        }
        for future in as_completed(futures_context_map):
            context = futures_context_map[future]
            answer: Dict = future.result()
            if answer.get("score") >= THRESHOLD_SCORE:
                answer["context"] = annotate(context, answer["start"], answer["end"])
                answer["source"] = title
                answers.append(answer)
    return answers


def get_answer(question: str, language: str, titles: List[str] = []):
    cache_key = f"question.{language}.{question}"
    if cache_key in cache:
        return json.loads(cache.get(cache_key))

    candidate_pages: List[str] = []
    if len(titles) > 0:
        candidate_pages = titles
    else:
        entities = find_entities(question)
        for title in entities:
            # Fetched content will be cached. So this is not a waste of time.
            if wiki.get_page_text(language, title):
                candidate_pages.append(title)
    if not len(candidate_pages):
        candidate_pages = wiki.search(question, language)

    answers = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(qa_worker, question, language, title)
            for title in candidate_pages
        ]
        for future in futures:
            worker_answers = future.result()
            answers += worker_answers

    answers = sorted(answers, reverse=True, key=lambda x: x.get("score"))
    if len(answers):
        final_answer = answers[0]
        final_answer.update({"searched_in": candidate_pages})
        cache.set(cache_key, json.dumps(final_answer))
        return final_answer
    else:
        return {
            "answer": "Sorry, Could not find an answer.",
            "searched_in": candidate_pages,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    args = sys.argv[1:]
    print(get_answer("Who built the Charminar?", "en", []))
    print(get_answer("Who built the Eiffel Tower?", "en", []))
    # print(get_answer("Who won World War II?", "en"))
    # response = get_questions(args[0], args[1])
    # print(response)
