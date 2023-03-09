import openai
import os
from dotenv import load_dotenv
import logging
from typing import Dict

load_dotenv()  # take environment variables from .env.

openai.api_key = os.getenv("OPENAI_API_KEY")


def create_response(prompt: str) -> Dict:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
    except openai.error.RateLimitError as e:
        logging.error(e)
        msg = "I am sorry, but the model is currently overloaded with other requests. Please try again."
        answer = {"choices": [{"text": msg}]}
    except openai.error.OpenAIError as e:
        logging.error(e)
        msg = "I am sorry, but I am unable to answer this question."
        answer = {"choices": [{"text": msg}]}
    return answer
