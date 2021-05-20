import uuid

import responses
from django.test import TestCase

from cards.models import Card, MagicSet, Printing

sample_scryfall_api_card_response = r"""{
  "object": "card",
  "id": "ce4ec853-411d-40a3-84a7-a62b3cb57cb3",
  "oracle_id": "09cc8709-fe10-472a-b05c-e89f3523018d",
  "multiverse_ids": [
    497532
  ],
  "mtgo_id": 84806,
  "tcgplayer_id": 226930,
  "cardmarket_id": 510985,
  "name": "Austere Command",
  "lang": "en",
  "released_at": "2020-11-20",
  "uri": "https://api.scryfall.com/cards/ce4ec853-411d-40a3-84a7-a62b3cb57cb3",
  "scryfall_uri": "https://scryfall.com/card/cmr/12/austere-command?utm_source=api",
  "layout": "normal",
  "highres_image": true,
  "image_uris": {
    "small": "https://c1.scryfall.com/file/scryfall-cards/small/front/c/e/ce4ec853-411d-40a3-84a7-a62b3cb57cb3.jpg?1608908685",
    "normal": "https://c1.scryfall.com/file/scryfall-cards/normal/front/c/e/ce4ec853-411d-40a3-84a7-a62b3cb57cb3.jpg?1608908685",
    "large": "https://c1.scryfall.com/file/scryfall-cards/large/front/c/e/ce4ec853-411d-40a3-84a7-a62b3cb57cb3.jpg?1608908685",
    "png": "https://c1.scryfall.com/file/scryfall-cards/png/front/c/e/ce4ec853-411d-40a3-84a7-a62b3cb57cb3.png?1608908685",
    "art_crop": "https://c1.scryfall.com/file/scryfall-cards/art_crop/front/c/e/ce4ec853-411d-40a3-84a7-a62b3cb57cb3.jpg?1608908685",
    "border_crop": "https://c1.scryfall.com/file/scryfall-cards/border_crop/front/c/e/ce4ec853-411d-40a3-84a7-a62b3cb57cb3.jpg?1608908685"
  },
  "mana_cost": "{4}{W}{W}",
  "cmc": 6,
  "type_line": "Sorcery",
  "oracle_text": "Choose two —\n• Destroy all artifacts.\n• Destroy all enchantments.\n• Destroy all creatures with converted mana cost 3 or less.\n• Destroy all creatures with converted mana cost 4 or greater.",
  "colors": [
    "W"
  ],
  "color_identity": [
    "W"
  ],
  "keywords": [],
  "legalities": {
    "standard": "not_legal",
    "future": "not_legal",
    "historic": "not_legal",
    "gladiator": "not_legal",
    "pioneer": "not_legal",
    "modern": "legal",
    "legacy": "legal",
    "pauper": "not_legal",
    "vintage": "legal",
    "penny": "not_legal",
    "commander": "legal",
    "brawl": "not_legal",
    "duel": "legal",
    "oldschool": "not_legal",
    "premodern": "not_legal"
  },
  "games": [
    "paper",
    "mtgo"
  ],
  "reserved": false,
  "foil": true,
  "nonfoil": true,
  "oversized": false,
  "promo": false,
  "reprint": true,
  "variation": false,
  "set": "cmr",
  "set_name": "Commander Legends",
  "set_type": "draft_innovation",
  "set_uri": "https://api.scryfall.com/sets/39de6fbf-1f11-48d0-8f04-f0407f6a0732",
  "set_search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Acmr&unique=prints",
  "scryfall_set_uri": "https://scryfall.com/sets/cmr?utm_source=api",
  "rulings_uri": "https://api.scryfall.com/cards/ce4ec853-411d-40a3-84a7-a62b3cb57cb3/rulings",
  "prints_search_uri": "https://api.scryfall.com/cards/search?order=released&q=oracleid%3A09cc8709-fe10-472a-b05c-e89f3523018d&unique=prints",
  "collector_number": "12",
  "digital": false,
  "rarity": "rare",
  "card_back_id": "0aeebaf5-8c7d-4636-9e82-8c27447861f7",
  "artist": "Anna Steinbauer",
  "artist_ids": [
    "3516496c-c279-4b56-8239-720683d03ae0"
  ],
  "illustration_id": "7c6a01f8-e1f6-4fe4-b275-b2582be98783",
  "border_color": "black",
  "frame": "2015",
  "full_art": false,
  "textless": false,
  "booster": true,
  "story_spotlight": false,
  "edhrec_rank": 197,
  "preview": {
    "source": "TVMovie.de",
    "source_uri": "https://www.tvmovie.de/news/magic-the-gathering-4-exklusive-preview-karten-aus-commander-legends-115162",
    "previewed_at": "2020-10-31"
  },
  "prices": {
    "usd": "1.65",
    "usd_foil": "1.79",
    "eur": "0.89",
    "eur_foil": "1.36",
    "tix": "0.07"
  },
  "related_uris": {
    "gatherer": "https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=497532",
    "tcgplayer_decks": "https://decks.tcgplayer.com/magic/deck/search?contains=Austere+Command&page=1&utm_campaign=affiliate&utm_medium=api&utm_source=scryfall",
    "edhrec": "https://edhrec.com/route/?cc=Austere+Command",
    "mtgtop8": "https://mtgtop8.com/search?MD_check=1&SB_check=1&cards=Austere+Command"
  },
  "purchase_uris": {
    "tcgplayer": "https://shop.tcgplayer.com/product/productsearch?id=226930&utm_campaign=affiliate&utm_medium=api&utm_source=scryfall",
    "cardmarket": "https://www.cardmarket.com/en/Magic/Products/Search?referrer=scryfall&searchString=Austere+Command&utm_campaign=card_prices&utm_medium=text&utm_source=scryfall",
    "cardhoarder": "https://www.cardhoarder.com/cards/84806?affiliate_id=scryfall&ref=card-profile&utm_campaign=affiliate&utm_medium=card&utm_source=scryfall"
  }
}"""


def card_named(name):
    return Card.objects.create(
        name=name,
        mana_cost=' ',
        id=uuid.uuid4(),
    )


def set_code(code):
    return MagicSet.objects.create(code=code, name='Set', id=uuid.uuid4())


class CardManagerScryfallTestCase(TestCase):
    def test_fetching_card_by_name(self):
        url = 'https://api.scryfall.com/cards/named?fuzzy=aust+com'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, sample_scryfall_api_card_response)
            card = Card.objects.get_or_fetch_printing_for_name("aust com")
        self.assertIsNotNone(card)

    def test_fetching_when_card_exists(self):
        url = 'https://api.scryfall.com/cards/named?fuzzy=austere+command'
        card = card_named("Austere Command")
        with responses.RequestsMock() as rm:
            rm.add('GET', url, sample_scryfall_api_card_response)
            printing = Card.objects.get_or_fetch_printing_for_name("Austere Command")
        self.assertEqual(card.id, printing.card_id)

    def test_fetching_when_card_and_printing_exist(self):
        card = card_named("Austere Command")
        card.type_line = 'Sorcery'
        card.save()
        magic_set = set_code('test')
        Printing.objects.create(card=card, magic_set=magic_set, image_url='')
        with responses.RequestsMock():
            printing = Card.objects.get_or_fetch_printing_for_name("Austere Command")
        self.assertEqual(card.id, printing.card_id)


class CardManagerTestCase(TestCase):

    def test_getting_by_name_with_existing_printing_returns_that(self):
        card = Card.objects.create(id=uuid.uuid4(), name='Test', mana_cost='None')
        magic_set = MagicSet.objects.create(id=uuid.uuid4(), name='Testing Set', code='tests')
        printing = Printing.objects.create(magic_set=magic_set, card=card)

        result = Card.objects.get_or_create_printing_for_name('Test')
        self.assertEqual(printing, result)

    def test_getting_by_name_no_printing(self):
        card = Card.objects.create(id=uuid.uuid4(), name='Test', mana_cost='None')
        printing = Card.objects.get_or_create_printing_for_name('Test')
        self.assertIsNotNone(printing)
        self.assertEqual(card, printing.card)

    def test_dummy_creation(self):
        result = Card.objects.get_or_create_printing_for_name('Test')
        self.assertIsNotNone(result)
        self.assertEqual('Test', result.card.name)
