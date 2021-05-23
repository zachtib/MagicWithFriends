import random

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from cards.models import Color
from .deckimporter import colorpair_from_set
from .models import CommanderJumpstartDeck, DualColoredDeck


# Create your views here.
def start(request):
    all_colors = [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]

    # Pick three random colors
    selected_colors = random.sample(all_colors, 3)

    selected_decks = []
    for color in selected_colors:
        matching_decks = CommanderJumpstartDeck.objects.filter(color=color)
        selected_deck: CommanderJumpstartDeck = random.choice(matching_decks)
        commander = selected_deck.commander
        printing = commander.printings.first()
        selected_decks.append({
            'id': selected_deck.id,
            'name': commander.name,
            'color': selected_deck.color,
            'slug': selected_deck.slug,
            'image_url': printing.image_url,
        })

    for item in selected_decks:
        passed = [deck['id'] for deck in selected_decks if deck['id'] != item['id']]
        url = reverse('cj-second-selection', args=[item['slug']])
        item['url'] = f'{url}?passed={",".join(str(i) for i in passed)}'

    return render(request, 'cmdrjump/first_selection.html', {
        'options': selected_decks,
    })


def make_second_selection(request, cmdr):
    passed_qs = request.GET.get('passed', None)
    if passed_qs is not None:
        passed = [int(i) for i in passed_qs.split(',')]
    else:
        passed = []
    first_selection: CommanderJumpstartDeck = get_object_or_404(CommanderJumpstartDeck, slug=cmdr)

    all_colors = [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]

    # noinspection PyTypeChecker
    all_colors.remove(first_selection.color)

    # Pick three random colors
    selected_colors = random.sample(all_colors, 3)

    selected_decks = []
    for color in selected_colors:
        matching_decks = CommanderJumpstartDeck.objects.filter(color=color).exclude(id__in=passed)
        selected_deck: CommanderJumpstartDeck = random.choice(matching_decks)
        commander = selected_deck.commander
        printing = commander.printings.first()
        selected_decks.append({
            'id': selected_deck.id,
            'name': commander.name,
            'color': selected_deck.color,
            'slug': selected_deck.slug,
            'image_url': printing.image_url,
        })

    for item in selected_decks:
        url = reverse('cj-result', args=[first_selection.slug, item['slug']])
        item['url'] = url

    return render(request, 'cmdrjump/second_selection.html', {
        'first_selection': first_selection,
        'options': selected_decks,
    })


def result(request, cmdr_1, cmdr_2):
    try:
        first_selection = CommanderJumpstartDeck.objects.prefetch_related('cards__card').get(slug=cmdr_1)
        second_selection = CommanderJumpstartDeck.objects.prefetch_related('cards__card').get(slug=cmdr_2)
        colors = colorpair_from_set({first_selection.color, second_selection.color})
        pair_deck = DualColoredDeck.objects.prefetch_related('cards__card').get(colors=colors)
    except (CommanderJumpstartDeck.DoesNotExist, DualColoredDeck.DoesNotExist):
        raise Http404()

    commanders = [first_selection.commander, second_selection.commander]

    deck_sections = {}

    for item in first_selection.cards.all():
        category = item.get_category_display()
        if category not in deck_sections.keys():
            deck_sections[category] = []
        deck_sections[category].append({
            'count': item.count,
            'card': item.card,
        })

    for item in second_selection.cards.all():
        category = item.get_category_display()
        if category not in deck_sections.keys():
            deck_sections[category] = []
        deck_sections[category].append({
            'count': item.count,
            'card': item.card,
        })

    for item in pair_deck.cards.all():
        category = item.get_category_display()
        if category not in deck_sections.keys():
            deck_sections[category] = []
        deck_sections[category].append({
            'count': 1,
            'card': item.card,
        })

    column_count = 0
    column_index = 0
    columns = [{}]
    for category, entries in deck_sections.items():
        columns[column_index][category] = entries
        column_count += sum(item['count'] for item in entries)
        if column_count > 30:
            column_index += 1
            columns.append({})
            column_count = 0

    return render(request, 'cmdrjump/results.html', {
        'commanders': commanders,
        'deck_sections': deck_sections,
        'columns': columns,
    })
