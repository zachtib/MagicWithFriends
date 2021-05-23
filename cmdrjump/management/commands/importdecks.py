from django.core.management import BaseCommand

from cmdrjump.deckimporter import importdecks


class Command(BaseCommand):

    def handle(self, *args, **options):
        importdecks()
