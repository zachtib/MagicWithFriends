from django.db import models
from django.utils.text import slugify

from cards.models import Color, Card, Type, ColorPair


class CommanderJumpstartDeck(models.Model):
    color = models.CharField(
        max_length=1,
        choices=Color.choices,
    )
    commander = models.ForeignKey(Card, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.slug = slugify(self.commander.name)[:50]
        super().save(force_insert, force_update, using, update_fields)


class CommanderJumpstartEntry(models.Model):
    deck = models.ForeignKey(CommanderJumpstartDeck, on_delete=models.CASCADE, related_name='cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='+')
    category = models.CharField(max_length=1, choices=Type.choices)
    count = models.IntegerField(default=1)


class DualColoredDeck(models.Model):
    colors = models.CharField(max_length=2, choices=ColorPair.choices, unique=True)

    def __str__(self):
        return f'{self.get_colors_display()} Color Pair Deck'


class DualColoredEntry(models.Model):
    deck = models.ForeignKey(DualColoredDeck, on_delete=models.CASCADE, related_name='cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='+')
    category = models.CharField(max_length=1, choices=Type.choices)
