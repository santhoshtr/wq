from __future__ import annotations

import json
import logging

import requests

logging.basicConfig(level=logging.INFO)

USER_AGENT = "wikiqa (https://wq.thottingal.in)"

logging.basicConfig(level=logging.INFO)

property_labels_data = json.load(open("wq/data/wikidata.props.en.json"))


class WikidataItem:
    def __init__(self, language, title) -> None:
        self.language = language
        self.title = title
        self.qid = None
        self.entity: list[dict] = None
        self.property_lookup = {}

    def fetch_qid(self):
        qid = None
        params = {"action": "wbsearchentities", "format": "json", "search": self.title, "language": self.language}
        data: list[dict] = requests.get(self.api_url, params=params, timeout=100).json()
        qid = data["search"][0]["id"]

        return qid

    def fetch_entity(self):
        if not self.qid:
            self.qid = self.fetch_qid()
        params = {"action": "wbgetentities", "format": "json", "ids": self.qid, "languages": self.language}
        data: list[dict] = requests.get(self.api_url, params=params, timeout=100).json()
        return data["entities"][self.qid]

    def get_properties(self):
        if not self.entity:
            self.entity = self.fetch_entity()
        if not self.property_lookup:
            self.get_property_lookup()
        claims = self.entity.get("claims")
        for property in claims:
            claim = claims[property]
            if not claim[0]:
                print("Where did that go?")
            property_def = self.property_lookup.get(property)
            print(property, property_def.get("label"), claim[0]["mainsnak"].get("datavalue", {}))

    def get_property_lookup(self):
        for item in property_labels_data:
            self.property_lookup[item.get("id")] = item

    @property
    def api_url(self):
        return "https://wikidata.org/w/api.php"


if __name__ == "__main__":
    wikdataitem = WikidataItem("en", "Barbie_(film)")
    wikdataitem.get_properties()
