from django.db import models


class Card(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=20)

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
