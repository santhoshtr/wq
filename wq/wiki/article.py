from __future__ import annotations

import logging
from hashlib import shake_256

import bs4
import httpx
import urllib

logging.basicConfig(level=logging.INFO)

USER_AGENT = "wikiqa (https://wq.thottingal.in)"

logging.basicConfig(level=logging.INFO)


class Article:
    def __init__(self, language, title) -> None:
        self.language = language
        self.title = title
        self.content = None
        self.metadata: list[dict] = None

    def get_sections(self):
        text_sections, html_sections = self.get_page_sections()
        if len(text_sections) == 0:
            raise Exception(f"Page does not exist? {self.language} - {self.title}")
        return text_sections, html_sections

    def _id(self, *argv):
        return int(shake_256("".join(argv).encode()).hexdigest(6), 16)

    @property
    def page_url(self):
        return f"https://{self.language.lower()}.wikipedia.org/wiki/{urllib.parse.quote(self.title)}"

    @property
    def api_url(self):
        return f"https://{self.language.lower()}.wikipedia.org/w/api.php"

    def get_page_metadata(self):
        api_url = f"https://{self.language}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(self.title)}"
        params = {"redirects":True}
        response = httpx.get(api_url,params=params, timeout=100,follow_redirects=True)

        self.metadata: list[dict] =response.json()

        if "title" not in self.metadata:
            return self.metadata
        self.metadata["language"] = self.metadata["lang"]
        self.metadata["url"] = self.metadata["content_urls"]["desktop"]["page"]
        if "thumbnail" in self.metadata:
            self.metadata["thumbnail"] = self.metadata["thumbnail"]["source"]
        del self.metadata["lang"]
        del self.metadata["namespace"]
        del self.metadata["titles"]
        del self.metadata["extract_html"]
        del self.metadata["content_urls"]
        if "originalimage" in self.metadata:
            del self.metadata["originalimage"]
        del self.metadata["extract"]
        del self.metadata["type"]
        if "coordinates" in self.metadata:
            del self.metadata["coordinates"]
        return self.metadata

    def get_page_sections(self, max_paragraphs: int = -1) -> str:
        """
        This function takes a wikipedia url and returns the text of the first 3 paragraphs

        Args:
            language (str): Wiki language. Defaults to en
            title (str): title
            max_paragraphs (int, optional): max paragraphs to use. Defaults to -1. -1 means all text.

        Returns:
            str: A string of the first 3 paragraphs of text

        """
        if not self.content:
            api_url = f"https://{self.language}.wikipedia.org/api/rest_v1/page/html/{urllib.parse.quote(self.title)}?redirect=true"
            response = httpx.get(api_url, timeout=100, follow_redirects=True)
            self.content = response.content

        soup = bs4.BeautifulSoup(self.content, "html.parser")
        sections = soup.select("section > p")
        text_sections = []
        html_sections = []
        for section in sections:
            if section.get_text().strip():
                text_sections.append(section.get_text().strip())
                html_sections.append(str(section))
        return text_sections, html_sections


if __name__ == "__main__":
    article = Article("en", "Oxygen")
    text, html = article.get_sections()

    print(len(text))
    print(len(html))
    print(text[4])
    print(html[4])
