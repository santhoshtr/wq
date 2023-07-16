import logging
import os
from typing import Dict

import openai
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
logging.basicConfig(level=logging.INFO)

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"

systemprompt = """
    You are a helpful assistant that reads the give text and provide
    all possible questions and answers in json format with "question" and "answer" as keys.
    You will base all your questions and answers only on the given text.
    """


def create_response(prompt_input: str) -> Dict:
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": systemprompt}, {"role": "user", "content": prompt_input}],
            temperature=0,
        )
        answer = response.choices[0].message.content
        logging.info(f"[ChatGPT] {response.usage.prompt_tokens} prompt tokens used.")
    except openai.error.RateLimitError as e:
        logging.error(e)
        msg = "I am sorry, but the model is currently overloaded with other requests. Please try again."
        answer = {"choices": [{"text": msg}]}
    except openai.error.OpenAIError as e:
        logging.error(e)
        msg = "I am sorry, but I am unable to answer this question."
        answer = {"choices": [{"text": msg}]}
    return answer
