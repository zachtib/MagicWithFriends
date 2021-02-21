import uuid

from django.test import TestCase

from cards.models import Card, MagicSet, Printing
from scryfall.client import ScryfallClient


class Throwaway(TestCase):
    def test_client(self):
        client = ScryfallClient()
        s = client.get_cards_for_set_code('thb')
        print(len(s))


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
