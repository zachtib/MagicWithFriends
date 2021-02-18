from django.test import TestCase

# Create your tests here.
from scryfall.client import ScryfallClient


class Throwaway(TestCase):
    def test_client(self):
        client = ScryfallClient()
        s = client.get_cards_for_set_code('thb')
        print(len(s))
