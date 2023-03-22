from api import chatgpt, wiki
from utils import find_entities,chunk
import json
import logging
import sys
import functools
from distillbertqa import onnx_qa
from typing import List,Dict
logging.basicConfig(level=logging.INFO)

@functools.cache
def get_questions(language, title: str):
    wiki_text = wiki.get_page_text(language,title,10)
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

def get_answer(question:str, language:str, titles: List[str]=[], threshold_score=0.9):
    candidate_pages:List[str]=[]
    if len(titles)>0:
        candidate_pages=titles
    candiate_pages_from_ne:List[str]=find_entities(question)
    candidate_pages_from_search:List[str]= wiki.search(question, language)
    candidate_pages:List[str]=candiate_pages_from_ne+candidate_pages_from_search
    for i, title in enumerate(candidate_pages):
        logging.info(f"[Wiki] {language}:{title} Searching for \"{question}\"")
        wiki_text = wiki.get_page_text(language, title)
        if not wiki_text:
            logging.info(f"Page does not exist? {language} - {title}")
            continue
        full_context = wiki_text.split("\n\n")
        context_chunks = list(chunk(full_context, 5))
        for context_chunk in context_chunks:
            context = "\n".join(context_chunk)
            if not context:
                continue
            answer:Dict=onnx_qa(question, context)
            if answer.get("score") >= threshold_score:
                chunk1 = context[answer["start"]-100:answer["start"]]
                chunk2 = context[answer["start"] : answer["end"]]
                chunk3 = context[ answer["end"]: answer["end"]+100]
                answer["context"]=f"{chunk1}<mark>{chunk2}</mark>{chunk3}"
                answer["source"]=title
                answer["searched_in"]=candidate_pages
                return answer
    return {
        "answer": "Sorry, Could not find an answer.",
        "searched_in": candidate_pages
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    args = sys.argv[1:]
    print(get_answer("Who build Charminar?", "en", []))
    print(get_answer("Who won World War II?", "en"))
    # response = get_questions(args[0], args[1])
    # print(response)
