from typing import List

from django.core.management import BaseCommand

from cards.models import MagicSet, Card, Printing
from scryfall.client import ScryfallClient
from scryfall.models import ScryfallSet, ScryfallCard


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'expansions',
            metavar='code',
            type=str,
            nargs='+',
            help='A list of expansion codes to update'
        )
        parser.add_argument(
            '--force',
            action='store_true'
        )

    def handle(self, *args, **options):
        expansions = options['expansions']
        forced = options['force']
        scryfall = ScryfallClient()
        for code in expansions:
            scryfall_set: ScryfallSet = scryfall.get_set(code)
            local_set, created = MagicSet.objects.get_or_create(code=code, defaults={
                'id': scryfall_set.id,
                'name': scryfall_set.name,
            })
            if forced and not created:
                local_set.name = scryfall_set.name
            print(f'Working with {local_set.name}')
            scryfall_cards: List[ScryfallCard] = scryfall.get_cards_for_set_code(code)
            for scryfall_card in scryfall_cards:
                local_card, created = Card.objects.get_or_create(id=scryfall_card.id, defaults={
                    'name': scryfall_card.name,
                    'mana_cost': scryfall_card.mana_cost,
                })
                if created:
                    print(f'Created: {local_card}')
                printing, created = Printing.objects.get_or_create(magic_set=local_set, card=local_card)
