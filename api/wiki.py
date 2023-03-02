import requests
import bs4

def get_wikipedia_text(url: str, paragraph_number: int = 10) -> str:
    """
    This function takes a wikipedia url and returns the text of the first 3 paragraphs

    Parameters
    ----------
    url : str
        The wikipedia url
    paragraph_number : int
        The number of paragraphs to extract from the article

    Returns
    -------
    paragraph_number : str
        A string of the first 3 paragraphs of text

    """

    page = requests.get(url, timeout=100)
    soup = bs4.BeautifulSoup(page.content, "html.parser")

    pars = soup.select("div.mw-parser-output > p")
    non_empty_pars = [par.text.strip() for par in pars if par.text.strip()][
        :paragraph_number
    ]
    text = "\n".join(non_empty_pars)

    return text

if __name__ == "__main__":
    text = get_wikipedia_text("https://en.wikipedia.org/wiki/Charminar")
    print(text)