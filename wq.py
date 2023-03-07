from api import chatgpt, wiki
import json
import logging

def get_questions(language, title:str):
    logging.info(f'[ChatGPT] Getting questions for {language} - {title}...')
    wiki_text = wiki.get_wikipedia_text(f"https://{language}.wikipedia.org/wiki/{title}")
    if not wiki_text:
        return []
    prompt = (
        # fstring with a variable called content and a variable called search_question
        f"""
        Act as if no information exists in the universe other than what is in this text:
        `{wiki_text}`
        Provide all possible questions and answers in json format with "question" and "answer" as keys.
        """
    )

    response = chatgpt.create_response(prompt)
    logging.info(f'[ChatGPT] Got questions for {language} - {title}')
    return json.loads(response)["questions"]

if __name__ == "__main__":
    response = get_questions( "en", "Charminar")
    print(response)