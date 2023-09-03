
import httpx


def search_wikipedia(query, wikicode='en') -> list[str]:
    url = f"https://{wikicode}.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'redirects': True,
        'srsearch': query,
        'srnamespace': 0,
        'srlimit': 2,
    }

    response = httpx.get(url, params=params)
    data = response.json()

    titles = [result['title'] for result in data['query']['search']]

    return titles

