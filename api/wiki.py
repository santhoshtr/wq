import logging

import bs4
import redis
import requests

cache = redis.Redis(host="localhost", port=6379)

logging.basicConfig(level=logging.INFO)

USER_AGENT = "wikiqa (https://wq.thottingal.in)"


def get_page_url(language, title):
    return f"https://{language.lower()}.wikipedia.org/wiki/{title}"


def get_api_url(language):
    return f"https://{language.lower()}.wikipedia.org/w/api.php"


def get_page_text(language, title: str, max_paragraphs: int = -1) -> str:
    """
    This function takes a wikipedia url and returns the text of the first 3 paragraphs

    Args:
        language (str): Wiki language. Defaults to en
        title (str): title
        max_paragraphs (int, optional): max paragraphs to use. Defaults to -1. -1 means all text.

    Returns:
        str: A string of the first 3 paragraphs of text

    """
    cache_key = f"page.content.{language}.{title}"
    if cache_key in cache:
        return cache.get(cache_key).decode()
    logging.info(f"[Wiki] Getting content for {language}:{title}")
    page = requests.get(get_page_url(language, title), timeout=100)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    text = ""
    elements = soup.findAll(["p", "h2"])
    for element in elements:
        if element.get_text().strip():
            if element.name == "h2":
                text += "\n\n"
            else:
                text += element.get_text().strip() + "\n"
    cache.set(cache_key, text)
    return text



if __name__ == "__main__":
    text = get_page_text("en", "Charminar")
    print(text)
