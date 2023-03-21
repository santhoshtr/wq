from api import chatgpt, wiki
import json
import logging
import sys
from distillbertqa import onnx_qa
logging.basicConfig(level=logging.INFO)

def get_questions(language, title: str):
    wiki_text = wiki.get_wikipedia_text(
        f"https://{language}.wikipedia.org/wiki/{title}"
    )
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

def get_answer(question, language, title: str):
    wiki_text = wiki.get_wikipedia_text(
        f"https://{language}.wikipedia.org/wiki/{title}"
    )
    if not wiki_text:
        logging.info(f"Page does not exist? {language} - {title}")
        return []
    context = wiki_text
    return onnx_qa(question, context)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    args = sys.argv[1:]
    print(get_answer("Who build Charminar?", "en", "Charminar"))
    # response = get_questions(args[0], args[1])
    # print(response)
