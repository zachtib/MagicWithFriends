import re
from pathlib import Path

from django.db import transaction

from cards.models import Card, Color, Type, ColorPair
from .models import CommanderJumpstartDeck, CommanderJumpstartEntry, DualColoredDeck, DualColoredEntry

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


def colorpair_from_set(colors):
    if 'W' in colors:
        if 'U' in colors:
            return ColorPair.WU
        elif 'B' in colors:
            return ColorPair.WB
        elif 'R' in colors:
            return ColorPair.RW
        elif 'G' in colors:
            return ColorPair.GW
    elif 'U' in colors:
        if 'B' in colors:
            return ColorPair.UB
        elif 'R' in colors:
            return ColorPair.UR
        elif 'G' in colors:
            return ColorPair.GU
    elif 'B' in colors:
        if 'R' in colors:
            return ColorPair.BR
        elif 'G' in colors:
            return ColorPair.BG
    elif 'R' in colors and 'G' in colors:
        return ColorPair.RG
    raise Exception(f'Asked for an invalid color pair: {colors}')


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
                if len(parsed_colors) == 0 and card.name == 'Rograkh, Son of Rohgahh':
                    # Handle a very special case
                    parsed_colors = {'R'}
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
        print(f'Imported {str(deck)}')
    else:
        # Treat this as a 2C Deck
        deck = DualColoredDeck()
        entries = []
        found_colors = set()
        for line in decklist:
            count, name = line.split(' ', maxsplit=1)
            printing = Card.objects.get_or_fetch_printing_for_name(name)
            card = printing.card
            count = int(count)  # Should always be 1
            assert count == 1
            if card.mana_cost is not None and card.mana_cost != '':
                card_colors = determine_colors_from_manacost(card.mana_cost)
                found_colors.update(card_colors)
            new_entry = DualColoredEntry(
                deck=deck,
                card=card,
                category=determine_category_from_card(card),
            )
            entries.append(new_entry)
        assert len(found_colors) == 2  # We need two colors here
        deck.colors = colorpair_from_set(found_colors)
        with transaction.atomic():
            deck.save()
            for entry in entries:
                entry.save()
        print(f'Imported {str(deck)}')


def importdecks():
    CommanderJumpstartDeck.objects.all().delete()
    DualColoredDeck.objects.all().delete()
    with open(FILENAME) as f:
        contents = f.read()
        decklists = [deck.splitlines() for deck in contents.split('\n\n')]
        for decklist in decklists:
            process_decklist(decklist)
