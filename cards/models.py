import uuid
from typing import Optional, List

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
    UNKNOWN = 'U', _('Unknown')


def color_string_from_colors(colors: Optional[List[str]]) -> str:
    if colors is None:
        return ''
    return ''.join(colors)[:5]


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

    def from_scryfall_card(self, scryfall_card: ScryfallCard, card: Optional['Card'] = None) -> 'Card':
        card = card or Card(id=scryfall_card.id)
        is_dfc = scryfall_card.card_faces is not None and len(scryfall_card.card_faces) > 1

        card.layout = scryfall_card.layout
        card.name = scryfall_card.name
        card.type_line = scryfall_card.type_line
        card.color_indicator = color_string_from_colors(scryfall_card.color_indicator)
        card.loyalty = scryfall_card.loyalty
        card.power = scryfall_card.power
        card.toughness = scryfall_card.toughness
        card.oracle_text = scryfall_card.oracle_text

        if scryfall_card.mana_cost is not None:
            card.mana_cost = scryfall_card.mana_cost
        elif is_dfc:
            mana_costs = []
            for face in scryfall_card.card_faces:
                if face.mana_cost is not None and face.mana_cost != '':
                    mana_costs.append(face.mana_cost)
            card.mana_cost = ' // '.join(mana_costs)

        faces = []
        if is_dfc:
            if card.faces.count() > 0:
                card.faces.all().delete()
            for index, face in enumerate(scryfall_card.card_faces):
                faces.append(self.from_scryfall_cardface(card, index, face))

        with transaction.atomic():
            card.save()
            if is_dfc:
                for face in faces:
                    face.save()
        return card

    def get_or_fetch_printing_for_name(self, name: str):
        scryfall_card = None
        queryset = self.get_queryset()
        try:
            card = queryset.get(name__iexact=name)
            if card.should_update():
                scryfall_card = scryfall_card or self.scryfall.get_card_by_name_fuzzy(name)
                card = self.from_scryfall_card(scryfall_card, card)
            printing = card.printings.first()
            if printing is not None:
                if 'ec8e4142' in printing.image_url and card.name != 'Totally Lost':
                    # Special case for the Totally Lost art
                    scryfall_card = scryfall_card or self.scryfall.get_card_by_name_fuzzy(name)
                    if scryfall_card.image_uris is not None:
                        printing.image_url = scryfall_card.image_uris.normal
                        printing.save()
                    elif scryfall_card.card_faces is not None and len(scryfall_card.card_faces) > 1:
                        face = scryfall_card.card_faces[0]
                        if face.image_uris is not None:
                            printing.image_url = face.image_uris.normal
                            printing.save()
                return printing
        except Card.DoesNotExist:
            card = None
        #  Card doesn't exist in our database, let's fetch it
        #  Handle DFCs
        if '/' in name:
            name, _ = name.split('/', maxsplit=1)
        scryfall_card = scryfall_card or self.scryfall.get_card_by_name_fuzzy(name)
        if card is None:
            card = self.from_scryfall_card(scryfall_card)
        s = scryfall_card.set_uri
        set_id = s[s.rindex('/') + 1:]
        magic_set, created = MagicSet.objects.get_or_create(code=scryfall_card.set, defaults={
            'name': scryfall_card.set_name,
            'id': set_id,
        })
        if scryfall_card.image_uris is not None:
            image_url = scryfall_card.image_uris.normal
        elif scryfall_card.card_faces is not None and len(scryfall_card.card_faces) > 1:
            face = scryfall_card.card_faces[0]
            if face.image_uris is not None:
                image_url = face.image_uris.normal
            else:
                raise Exception(f'Could not find a card image for {scryfall_card}')
        else:
            raise Exception(f'Could not find a card image for {scryfall_card}')

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
    layout = models.CharField(max_length=20, default='normal')
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=20, null=True, blank=True)
    type_line = models.CharField(max_length=200)
    color_indicator = models.CharField(max_length=5, null=True, blank=True)
    loyalty = models.CharField(max_length=5, null=True, blank=True)
    oracle_text = models.TextField(blank=True, null=True)
    power = models.CharField(max_length=5, null=True, blank=True)
    toughness = models.CharField(max_length=5, null=True, blank=True)

    def should_update(self) -> bool:
        if self.type_line == '':
            return True
        return False

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
    type_line = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return self.name


class Printing(models.Model):
    magic_set = models.ForeignKey(MagicSet, on_delete=models.CASCADE, related_name='printings')
    card = models.ForeignKey(Card, related_name='printings', on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f'{self.card.name} in {self.magic_set.name}'
