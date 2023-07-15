import logging
from typing import List

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


def search(query: str, language="en", max_results=5) -> List[str]:
    """Query wikipedia and extract titles that might answer the query

    Args:
        query (str): Search query
        language (str): Wiki language. Defaults to en
        max_results (int, optional): _description_. Defaults to 5.

    Returns:
        List[str]: List of article titles that are relevant to the query
    """

    cache_key = f"query.{language}.{query}"
    if cache_key in cache:
        return [v.decode() for v in cache.zrange(cache_key, 0, -1)]
    headers = {"User-Agent": USER_AGENT}
    search_params = {
        "action": "query",
        "list": "search",
        "srprop": "",
        "srlimit": max_results,
        "srsearch": query,
        "format": "json",
        "origin": "*",
    }
    r = requests.get(get_api_url(language), params=search_params, headers=headers)
    raw_results = r.json()

    if "error" in raw_results:
        raise Exception(raw_results["error"]["info"])

    search_results = (d["title"] for d in raw_results["query"]["search"])
    pages = list(search_results)
    for i, page in enumerate(pages):
        cache.zadd(cache_key, {page: i})
    return pages


if __name__ == "__main__":
    pages = search("Who built Charminar?", "en")
    print(pages)
    text = get_page_text("en", "Charminar")
    print(text)
