from django.core.management import BaseCommand

from dungeons.dungeonimporter import importdungeons


class Command(BaseCommand):

    def handle(self, *args, **options):
        importdungeons()
