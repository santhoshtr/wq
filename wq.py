from api import chatgpt, wiki
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
def get_questions(language, title: str):
    logging.info(f"[ChatGPT] Getting questions for {language} - {title}...")
    wiki_text = wiki.get_wikipedia_text(
        f"https://{language}.wikipedia.org/wiki/{title}"
    )
    if not wiki_text:
        logging.info(f"Page does not exist? {language} - {title}")
        return []
    prompt = (
        f"""
        Act as if no information exists in the universe other than what is in this text:
        `{wiki_text}`
        Provide all possible questions and answers in json format with "question" and "answer" as keys.
        """
    )

    responseStr = chatgpt.create_response(prompt)
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



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    args = sys.argv[1:]
    response = get_questions(args[0], args[1])
    print(response)
