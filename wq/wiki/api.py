import httpx


def search_wikipedia(query, wikicode="en") -> list[str]:
    url = f"https://{wikicode}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "redirects": True,
        "srsearch": query,
        "srnamespace": 0,
        "srlimit": 2,
    }

    response = httpx.get(url, params=params)
    data = response.json()

    titles = [result["title"] for result in data["query"]["search"]]

    return titles


def get_plain_text(title, wikicode="en"):
    url = f"https://{wikicode}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|revisions",
        "rvprop": "ids",
        "titles": title,
        "redirects": True,
        "explaintext": True,
        "formatversion": 2,
    }

    response = httpx.get(url, params=params, timeout=100, follow_redirects=True)
    data = response.json()
    page = data["query"]["pages"][0]
    revision = page["revisions"][0]["revid"]
    text_content = page["extract"]

    return revision, text_content
