from __future__ import annotations

import logging
import urllib
from typing import List

from sentencesegmenter import segment

from wq.types import ArticleSection

from .api import get_plain_text

logging.basicConfig(level=logging.INFO)

USER_AGENT = "wikiqa (https://wq.thottingal.in)"

logging.basicConfig(level=logging.INFO)


class Article:
    def __init__(self, language, title) -> None:
        self.language = language
        self.title = title
        self.content = None
        self.revision: int = 0

    def get_sections(self) -> List[ArticleSection]:
        text_sections: List[ArticleSection] = self.get_page_sections()
        if len(text_sections) == 0:
            raise Exception(f"Page does not exist? {self.language} - {self.title}")
        return text_sections

    def page_url(self):
        return f"https://{self.language.lower()}.wikipedia.org/wiki/{urllib.parse.quote(self.title)}"

    @property
    def api_url(self):
        return f"https://{self.language.lower()}.wikipedia.org/w/api.php"

    def get_page_sections(self) -> List[ArticleSection]:
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
            self.revision, self.content = get_plain_text(self.title, self.language)
        raw_sections = self.content.split("\n")
        sections: List[ArticleSection] = []
        for section in raw_sections:
            if not section.startswith("==") and len(section.strip()):
                sections.append(ArticleSection(section=section, sentences=segment(self.language, section)))

        return sections


if __name__ == "__main__":
    article = Article("en", "Oxygen")
    sections = article.get_sections()

    print(len(sections))
    print(sections[0])
