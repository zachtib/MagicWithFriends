import responses
from django.test import TestCase

from scryfall.client import ScryfallClient

sets_response = r"""{
  "object": "list",
  "has_more": false,
  "data": [
    {
      "object": "set",
      "id": "5064a720-907f-4cb6-a425-766dc1dd7374",
      "code": "sta",
      "mtgo_code": "sta",
      "arena_code": "sta",
      "name": "Strixhaven Mystical Archive",
      "uri": "https://api.scryfall.com/sets/5064a720-907f-4cb6-a425-766dc1dd7374",
      "scryfall_uri": "https://scryfall.com/sets/sta",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Asta&unique=prints",
      "released_at": "2021-04-23",
      "set_type": "masterpiece",
      "card_count": 6,
      "parent_set_code": "stx",
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/default.svg?1613365200"
    },
    {
      "object": "set",
      "id": "541c3c28-8747-40e5-a231-8e8f33234859",
      "code": "stx",
      "mtgo_code": "stx",
      "arena_code": "stx",
      "tcgplayer_id": 2773,
      "name": "Strixhaven: School of Mages",
      "uri": "https://api.scryfall.com/sets/541c3c28-8747-40e5-a231-8e8f33234859",
      "scryfall_uri": "https://scryfall.com/sets/stx",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Astx&unique=prints",
      "released_at": "2021-04-23",
      "set_type": "expansion",
      "card_count": 5,
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/stx.svg?1613365200"
    },
    {
      "object": "set",
      "id": "11e90d1b-0502-43e6-b056-e24836523c13",
      "code": "tsr",
      "tcgplayer_id": 2772,
      "name": "Time Spiral Remastered",
      "uri": "https://api.scryfall.com/sets/11e90d1b-0502-43e6-b056-e24836523c13",
      "scryfall_uri": "https://scryfall.com/sets/tsr",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Atsr&unique=prints",
      "released_at": "2021-03-19",
      "set_type": "masters",
      "card_count": 5,
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/tsr.svg?1613365200"
    },
    {
      "object": "set",
      "id": "a35fb0b2-03c1-426d-90ab-fbf9f5b19dc7",
      "code": "pkhc",
      "name": "Kaldheim Commander Promos",
      "uri": "https://api.scryfall.com/sets/a35fb0b2-03c1-426d-90ab-fbf9f5b19dc7",
      "scryfall_uri": "https://scryfall.com/sets/pkhc",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Apkhc&unique=prints",
      "released_at": "2021-02-05",
      "set_type": "promo",
      "card_count": 0,
      "parent_set_code": "khc",
      "digital": false,
      "nonfoil_only": true,
      "foil_only": true,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/khc.svg?1613365200"
    },
    {
      "object": "set",
      "id": "4d7b6bf0-0ded-49a0-8c0e-b1ae2bfba77c",
      "code": "pkhm",
      "name": "Kaldheim Promos",
      "uri": "https://api.scryfall.com/sets/4d7b6bf0-0ded-49a0-8c0e-b1ae2bfba77c",
      "scryfall_uri": "https://scryfall.com/sets/pkhm",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Apkhm&unique=prints",
      "released_at": "2021-02-05",
      "set_type": "promo",
      "card_count": 153,
      "parent_set_code": "khm",
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/khm.svg?1613365200"
    },
    {
      "object": "set",
      "id": "d532ef25-e52b-4276-941a-3a1c095544b0",
      "code": "khc",
      "tcgplayer_id": 2766,
      "name": "Kaldheim Commander",
      "uri": "https://api.scryfall.com/sets/d532ef25-e52b-4276-941a-3a1c095544b0",
      "scryfall_uri": "https://scryfall.com/sets/khc",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Akhc&unique=prints",
      "released_at": "2021-02-05",
      "set_type": "commander",
      "card_count": 119,
      "parent_set_code": "khm",
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/khc.svg?1613365200"
    },
    {
      "object": "set",
      "id": "43057fad-b1c1-437f-bc48-0045bce6d8c9",
      "code": "khm",
      "mtgo_code": "khm",
      "arena_code": "khm",
      "tcgplayer_id": 2750,
      "name": "Kaldheim",
      "uri": "https://api.scryfall.com/sets/43057fad-b1c1-437f-bc48-0045bce6d8c9",
      "scryfall_uri": "https://scryfall.com/sets/khm",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Akhm&unique=prints",
      "released_at": "2021-02-05",
      "set_type": "expansion",
      "card_count": 405,
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/khm.svg?1613365200"
    },
    {
      "object": "set",
      "id": "d44c4073-9771-4a9a-a304-317591f3de8c",
      "code": "tkhc",
      "tcgplayer_id": 2766,
      "name": "Kaldheim Commander Tokens",
      "uri": "https://api.scryfall.com/sets/d44c4073-9771-4a9a-a304-317591f3de8c",
      "scryfall_uri": "https://scryfall.com/sets/tkhc",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Atkhc&unique=prints",
      "released_at": "2021-02-05",
      "set_type": "token",
      "card_count": 8,
      "parent_set_code": "khc",
      "digital": false,
      "nonfoil_only": true,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/khc.svg?1613365200"
    },
    {
      "object": "set",
      "id": "c3ee48f1-6f93-42d4-b05c-65a04d02a488",
      "code": "tkhm",
      "name": "Kaldheim Tokens",
      "uri": "https://api.scryfall.com/sets/c3ee48f1-6f93-42d4-b05c-65a04d02a488",
      "scryfall_uri": "https://scryfall.com/sets/tkhm",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Atkhm&unique=prints",
      "released_at": "2021-02-05",
      "set_type": "token",
      "card_count": 23,
      "parent_set_code": "khm",
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/khm.svg?1613365200"
    },
    {
      "object": "set",
      "id": "dc1dbedc-9604-4c3a-886a-7be05f7e006a",
      "code": "pl21",
      "name": "2021 Lunar New Year",
      "uri": "https://api.scryfall.com/sets/dc1dbedc-9604-4c3a-886a-7be05f7e006a",
      "scryfall_uri": "https://scryfall.com/sets/pl21",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Apl21&unique=prints",
      "released_at": "2021-01-25",
      "set_type": "promo",
      "card_count": 2,
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/star.svg?1613365200"
    },
    {
      "object": "set",
      "id": "44c67c2c-7c14-4853-8dad-943a60816a05",
      "code": "j21",
      "name": "Judge Gift Cards 2021",
      "uri": "https://api.scryfall.com/sets/44c67c2c-7c14-4853-8dad-943a60816a05",
      "scryfall_uri": "https://scryfall.com/sets/j21",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Aj21&unique=prints",
      "released_at": "2021-01-01",
      "set_type": "promo",
      "card_count": 2,
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/default.svg?1613365200"
    },
    {
      "object": "set",
      "id": "4de7b6af-43e2-4cd8-990e-3927b65ba62f",
      "code": "cc1",
      "tcgplayer_id": 2699,
      "name": "Commander Collection: Green",
      "uri": "https://api.scryfall.com/sets/4de7b6af-43e2-4cd8-990e-3927b65ba62f",
      "scryfall_uri": "https://scryfall.com/sets/cc1",
      "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Acc1&unique=prints",
      "released_at": "2020-12-04",
      "set_type": "from_the_vault",
      "card_count": 8,
      "digital": false,
      "nonfoil_only": false,
      "foil_only": false,
      "icon_svg_uri": "https://c2.scryfall.com/file/scryfall-symbols/sets/cc1.svg?1613365200"
    }
  ]
}
"""


class ScryfallClientTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.client = ScryfallClient()

    def test_get_sets(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', 'https://api.scryfall.com/sets', sets_response)
            sets = self.client.get_sets()
        self.assertEqual(12, len(sets))
        first = sets[0]
        self.assertEqual('Strixhaven Mystical Archive', first.name)
        self.assertEqual('sta', first.code)
