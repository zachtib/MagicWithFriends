import uuid

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from scryfall.client import ScryfallClient
from scryfall.models import ScryfallCard, ScryfallCardFace


class Color(models.TextChoices):
    WHITE = 'W', _('White')
    BLUE = 'U', _('Blue')
    BLACK = 'B', _('Black')
    RED = 'R', _('Red')
    GREEN = 'G', _('Green')
    COLORLESS = 'C', _('Colorless')


class ColorPair(models.TextChoices):
    WU = 'WU', _('White / Blue')
    UB = 'UB', _('Blue / Black')
    BR = 'BR', _('Black / Red')
    RG = 'RG', _('Red / Green')
    GW = 'GW', _('Green / White')
    WB = 'WB', _('White / Black')
    BG = 'BG', _('Black / Green')
    GU = 'GU', _('Green / Blue')
    UR = 'UR', _('Blue / Red')
    RW = 'RW', _('Red / White')


class Type(models.TextChoices):
    CREATURE = 'C', _('Creature')
    PLANESWALKER = 'P', _('Planeswalker')
    SORCERY = 'S', _('Sorcery')
    INSTANT = 'I', _('Instant')
    ARTIFACT = 'A', _('Artifact')
    ENCHANTMENT = 'E', _('Enchantment')
    LAND = 'L', _('Land')


class CardManager(models.Manager):

    def __init__(self):
        super().__init__()
        self.scryfall = ScryfallClient()

    def from_scryfall_cardface(self, parent_card, index, scryfall_face: ScryfallCardFace) -> 'CardFace':
        card_face = CardFace(
            card=parent_card,
            index=index,
            name=scryfall_face.name,
            mana_cost=scryfall_face.mana_cost
        )
        return card_face

    def from_scryfall_card(self, scryfall_card: ScryfallCard) -> 'Card':
        is_dfc = scryfall_card.card_faces is not None and len(scryfall_card.card_faces) > 1
        new_card = Card(id=scryfall_card.id, name=scryfall_card.name)
        faces = []
        if is_dfc:
            mana_costs = []
            for index, face in enumerate(scryfall_card.card_faces):
                if face.mana_cost is not None and face.mana_cost != '':
                    mana_costs.append(face.mana_cost)
                faces.append(self.from_scryfall_cardface(new_card, index, face))
            new_card.mana_cost = ' // '.join(mana_costs)
        else:
            new_card.mana_cost = scryfall_card.mana_cost
        with transaction.atomic():
            new_card.save()
            if is_dfc:
                for face in faces:
                    face.save()
        return new_card

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
        #  Handle DFCs
        name, _ = name.split('/', maxsplit=1)
        scryfall_card = self.scryfall.get_card_by_name_fuzzy(name)
        if card is None:
            card = self.from_scryfall_card(scryfall_card)
        s = scryfall_card.set_uri
        set_id = s[s.rindex('/') + 1:]
        magic_set, created = MagicSet.objects.get_or_create(code=scryfall_card.set, defaults={
            'name': scryfall_card.set_name,
            'id': set_id,
        })
        if scryfall_card.card_faces is not None and len(scryfall_card.card_faces) > 1:
            face = scryfall_card.card_faces[0]
            image_url = face.image_uris.normal
        else:
            image_url = scryfall_card.image_uris.normal
        printing = Printing.objects.create(
            magic_set=magic_set,
            card=card,
            image_url=image_url
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
    index = models.IntegerField(default=0)
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=20, blank=True, null=True)


class Printing(models.Model):
    magic_set = models.ForeignKey(MagicSet, on_delete=models.CASCADE, related_name='printings')
    card = models.ForeignKey(Card, related_name='printings', on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f'{self.card.name} in {self.magic_set.name}'
