from typing import List

import requests

from .models import ScryfallCard, ScryfallSet


class ScryfallClient(object):
    __BASE_URL = 'https://api.scryfall.com'

    def __init__(self):
        pass

    def expand_url(self, url):
        return self.__BASE_URL + url

    def fetch_one(self, cls, url):
        if not hasattr(cls, 'from_dict'):
            raise AttributeError(f'{cls} has no attribute "from_dict"')
        response = requests.get(self.expand_url(url))
        if response.status_code != 200:
            raise RuntimeError(f'Received a non-200 response from Scryfall: {response.content}')
        json = response.json()
        return cls.from_dict(json)

    def fetch_many(self, cls, url):
        if not hasattr(cls, 'from_dict'):
            raise AttributeError(f'{cls} has no attribute "from_dict"')
        result = []
        should_continue = True
        request_url = self.expand_url(url)
        while should_continue:
            response = requests.get(request_url)
            if response.status_code != 200:
                raise RuntimeError(f'Received a non-200 response from Scryfall: {response.content}')
            json = response.json()
            data = json['data']
            for item in data:
                result_object = cls.from_dict(item)
                result.append(result_object)
            should_continue = json['has_more']
            if should_continue:
                request_url = json['next_page']
        return result

    def get_set(self, code) -> ScryfallSet:
        return self.fetch_one(ScryfallSet, f'/sets/{code}')

    def get_sets(self) -> List[ScryfallSet]:
        return self.fetch_many(ScryfallSet, '/sets')

    def get_card_by_name_fuzzy(self, name: str) -> ScryfallCard:
        name = name.replace(' ', '+')
        return self.fetch_one(ScryfallCard, f'/cards/named?fuzzy={name}')

    def get_cards_for_set_code(self, code) -> List[ScryfallCard]:
        url = f'/cards/search?order=spoiled&q=e={code}&unique=card'
        return self.fetch_many(ScryfallCard, url)

    def __scryfall_request(self, url, mapper):
        result = list()
        response = requests.get(self.expand_url(url))
        if response.status_code != 200:
            # TODO: Log a warning here
            return result
        json = response.json()
        data = json['data']
        for item in data:
            result_object = mapper(item)
            result.append(result_object)
        return result

    def get_all_sets(self) -> List[ScryfallSet]:
        return self.__scryfall_request('/sets', ScryfallSet.from_dict)

    def get_all_cards_for_set_code(self, code) -> List[ScryfallCard]:
        url = f'/cards/search?order=spoiled&q=e={code}&unique=card'
        return self.__scryfall_request(url, ScryfallCard.from_dict)
