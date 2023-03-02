from api import chatgpt, wiki
import json

def get_questions(title:str, language="en"):
    wiki_text = wiki.get_wikipedia_text(f"https://{language}.wikipedia.org/wiki/{title}")
    prompt = (
        # fstring with a variable called content and a variable called search_question
        f"""
        Act as if no information exists in the universe other that what is in this text:
        `{wiki_text}`
        Provide all possible questions and answers in json format with "question" and "answer" as keys.
        """
    )

    response = chatgpt.create_response(prompt)
    # print("*"+response+"*")
    return json.loads(response)["questions"]

if __name__ == "__main__":
    response = get_questions("Charminar", "en")
    print(response)