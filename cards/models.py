import uuid

from django.db import models

from scryfall.client import ScryfallClient
from scryfall.models import ScryfallCard


class CardManager(models.Manager):

    def __init__(self):
        super().__init__()
        self.scryfall = ScryfallClient()

    def from_scryfall_card(self, card: ScryfallCard) -> 'Card':
        return Card.objects.create(
            id=card.id,
            name=card.name,
            mana_cost=card.mana_cost
        )

    def get_or_fetch_printing_for_name(self, name: str):
        queryset = self.get_queryset()
        try:
            card = queryset.get(name__iexact=name)
            printing = card.printings.first()
            if printing is not None:
                return printing
        except Card.DoesNotExist:
            card = None
        #  Card doesn't exist in our database, let's fetch it
        scryfall_card = self.scryfall.get_card_by_name_fuzzy(name)
        if card is None:
            card = self.from_scryfall_card(scryfall_card)
        s = scryfall_card.set_uri
        set_id = s[s.rindex('/') + 1:]
        magic_set, created = MagicSet.objects.get_or_create(code=scryfall_card.set, defaults={
            'name': scryfall_card.set_name,
            'id': set_id,
        })
        printing = Printing.objects.create(
            magic_set=magic_set,
            card=card,
            image_url=scryfall_card.image_uris.normal
        )
        return printing

    def get_or_create_printing_for_name(self, name):
        queryset = self.get_queryset()
        card, created = queryset.get_or_create(name=name, defaults={
            'id': uuid.uuid4(),
            'mana_cost': 'N/A',
        })
        if not created:
            printing = card.printings.first()
            if printing is not None:
                return printing
        # We didn't get a printing, so lets fake one.
        magic_set, created = MagicSet.objects.get_or_create(code='tests', defaults={
            'id': uuid.uuid4(),
            'name': 'Testing Set',
        })
        printing = card.printings.create(magic_set=magic_set, card=card)
        return printing


class Card(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=20, blank=True, null=True)

    objects = CardManager()

    def __str__(self):
        return self.name


class MagicSet(models.Model):
    id = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)
    cards = models.ManyToManyField(Card, through='Printing')

    def get_absolute_url(self):
        from django.shortcuts import reverse
        return reverse('set-detail', args=[self.id])

    def __str__(self):
        return self.name


class CardFace(models.Model):
    card = models.ForeignKey(Card, related_name='faces', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=20, blank=True, null=True)


class Printing(models.Model):
    magic_set = models.ForeignKey(MagicSet, on_delete=models.CASCADE, related_name='printings')
    card = models.ForeignKey(Card, related_name='printings', on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f'{self.card.name} in {self.magic_set.name}'
