import uuid
from random import shuffle
from typing import List

from django.contrib.auth.models import User
from django.db import models

from cards.models import Printing, Card


class CubeNotLargeEnoughException(BaseException):
    pass


class Cube(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    default_pack_count = models.IntegerField(default=3)
    default_pack_size = models.IntegerField(default=15)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.shortcuts import reverse
        return reverse('cube-detail', args=[self.id])

    def bulk_update(self, card_names):
        self.entries.all().delete()
        for card_name in card_names:
            printing = Card.objects.get_or_create_printing_for_name(card_name)
            self.entries.create(card=printing, count=1)

    def calculate_size(self) -> int:
        return sum(self.entries.values_list('count', flat=True))

    def generate_packs(self, pack_count=None, pack_size=None) -> List[List[uuid.UUID]]:
        if pack_count is None:
            pack_count = self.default_pack_count
        if pack_size is None:
            pack_size = self.default_pack_size
        packs = []
        total_requested_cards = pack_count * pack_size
        cube_size = self.calculate_size()
        if total_requested_cards > cube_size:
            raise CubeNotLargeEnoughException()
        card_pool = []
        for entry in self.entries.all():
            for _ in range(entry.count):
                card_pool.append(entry.card.card.id)
        shuffle(card_pool)
        for _ in range(pack_count):
            pack = []
            for _ in range(pack_size):
                pack.append(card_pool.pop())
            packs.append(pack)
        return packs


class CubeEntry(models.Model):
    cube = models.ForeignKey(Cube, related_name='entries', on_delete=models.CASCADE)
    card = models.ForeignKey(Printing, related_name='+', on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    def get_card_name(self):
        return self.card.card.name
