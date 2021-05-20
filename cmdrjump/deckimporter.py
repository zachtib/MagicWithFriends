import re
from pathlib import Path

from django.db import transaction

from cards.models import Card, Color, Type
from .models import CommanderJumpstartDeck, CommanderJumpstartEntry

FILENAME = Path(__file__).resolve().parent / 'decklists.txt'


def determine_colors_from_manacost(cost):
    result = set()
    for character in re.findall(r'{(W|U|B|R|G)}', cost):
        if character == 'W':
            result.add(Color.WHITE)
        elif character == 'U':
            result.add(Color.BLUE)
        elif character == 'B':
            result.add(Color.BLACK)
        elif character == 'R':
            result.add(Color.RED)
        elif character == 'G':
            result.add(Color.GREEN)
    return result


def determine_category_from_card(card: Card):
    # TODO
    return Type.CREATURE


def process_decklist(decklist):
    is_commander_list = any(line.startswith('C') for line in decklist)
    if is_commander_list:
        deck = CommanderJumpstartDeck()
        entries = []
        for line in decklist:
            count, name = line.split(' ', maxsplit=1)
            printing = Card.objects.get_or_fetch_printing_for_name(name)
            card = printing.card
            if count == 'C':
                deck.commander = card
                parsed_colors = determine_colors_from_manacost(card.mana_cost)
                assert len(parsed_colors) == 1
                deck.color = list(parsed_colors)[0]
            else:
                count = int(count)
                new_entry = CommanderJumpstartEntry(
                    deck=deck,
                    card=card,
                    category=determine_category_from_card(card),
                    count=count
                )
                entries.append(new_entry)
        with transaction.atomic():
            deck.save()
            for entry in entries:
                entry.save()
    else:
        pass


def importdecks():
    CommanderJumpstartDeck.objects.all().delete()
    with open(FILENAME) as f:
        contents = f.read()
        decklists = [deck.splitlines() for deck in contents.split('\n\n')]
        for decklist in decklists:
            process_decklist(decklist)
