import uuid

from django.db import models


class CardManager(models.Manager):

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
    mana_cost = models.CharField(max_length=20)

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
    mana_cost = models.CharField(max_length=20)


class Printing(models.Model):
    magic_set = models.ForeignKey(MagicSet, on_delete=models.CASCADE, related_name='printings')
    card = models.ForeignKey(Card, related_name='printings', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.card.name} in {self.magic_set.name}'
