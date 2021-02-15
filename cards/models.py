from django.db import models


class MagicSet(models.Model):
    id = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=100)


class Card(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=20)


class CardFace(models.Model):
    card = models.ForeignKey(Card, related_name='faces', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=20)


class Printing(models.Model):
    magic_set = models.ForeignKey(MagicSet, related_name='printings', on_delete=models.CASCADE)
    card = models.ForeignKey(Card, related_name='printings', on_delete=models.CASCADE)
