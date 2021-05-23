import uuid
from unittest.mock import patch

import responses
from django.test import Client, TestCase
from parameterized import parameterized

from cards.models import Card, Color, ColorPair, Type, MagicSet, Printing
from cmdrjump.deckimporter import determine_colors_from_manacost, determine_category_from_card, colorpair_from_set, \
    process_decklist
from cmdrjump.models import CommanderJumpstartDeck, DualColoredDeck, CommanderJumpstartEntry, DualColoredEntry
import uuid
from unittest.mock import patch

import responses
from django.test import Client, TestCase
from parameterized import parameterized

from cards.models import Card, Color, ColorPair, Type, MagicSet, Printing
from cmdrjump.deckimporter import determine_colors_from_manacost, determine_category_from_card, colorpair_from_set, \
    process_decklist
from cmdrjump.models import CommanderJumpstartDeck, DualColoredDeck, CommanderJumpstartEntry, DualColoredEntry


def create_mock_card_response(card_name, mana_cost, type_line):
    scryfall_id = uuid.uuid4()
    return '''
        {
            "object": "card",
            "id": "%s",
            "lang": "en",
            "oracle_id": "ed66cd31-958f-4b28-82a3-e04acc819afc",
            "uri": "https://api.scryfall.com/cards/%s",
            "name": "%s",
            "mana_cost": "%s",
            "scryfall_uri": "https://scryfall.com/card/dom/113/yargle-glutton-of-urborg?utm_source=api",
            "layout": "normal",
            "type_line": "%s",
            "oracle_text": "",
            "set": "test",
            "set_name": "Testing",
            "set_uri": "https://api.scryfall.com/sets/39de6fbf-1f11-48d0-8f04-f0407f6a0732",
            "image_uris": {
                "small": "https://c1.scryfall.com/file/scryfall-cards/small/front/6/4/645cfc1b-76f2-4823-9fb0-03cb009f8b32.jpg?1562736801",
                "normal": "https://c1.scryfall.com/file/scryfall-cards/normal/front/6/4/645cfc1b-76f2-4823-9fb0-03cb009f8b32.jpg?1562736801",
                "large": "https://c1.scryfall.com/file/scryfall-cards/large/front/6/4/645cfc1b-76f2-4823-9fb0-03cb009f8b32.jpg?1562736801",
                "png": "https://c1.scryfall.com/file/scryfall-cards/png/front/6/4/645cfc1b-76f2-4823-9fb0-03cb009f8b32.png?1562736801",
                "art_crop": "https://c1.scryfall.com/file/scryfall-cards/art_crop/front/6/4/645cfc1b-76f2-4823-9fb0-03cb009f8b32.jpg?1562736801",
                "border_crop": "https://c1.scryfall.com/file/scryfall-cards/border_crop/front/6/4/645cfc1b-76f2-4823-9fb0-03cb009f8b32.jpg?1562736801"
            }
        }
        '''.strip() % (scryfall_id, scryfall_id, card_name, mana_cost, type_line)


class ManaCostTestCase(TestCase):

    def test_mono_color(self):
        result = determine_colors_from_manacost('{4}{W}')
        self.assertEqual({Color.WHITE}, result)

    def test_dual_color(self):
        result = determine_colors_from_manacost('{2}{U}{B}}')
        self.assertEqual({Color.BLUE, Color.BLACK}, result)

    def test_three_color(self):
        result = determine_colors_from_manacost('{1}{B}{R}}{G}')
        self.assertEqual({Color.BLACK, Color.RED, Color.GREEN}, result)

    def test_repeated_colors(self):
        result = determine_colors_from_manacost('{4}{W}{W}')
        self.assertEqual({Color.WHITE}, result)

    def test_colorless(self):
        result = determine_colors_from_manacost('{6}')
        self.assertEqual(set(), result)


class CardCategorizerTestCase(TestCase):

    @parameterized.expand([
        ('Creature - Elf', Type.CREATURE),
        ('Artifact Creature - Construct', Type.CREATURE),
        ('Enchantment Creature - Dryad', Type.CREATURE),
        ('Artifact', Type.ARTIFACT),
        ('Basic Land - Mountain', Type.LAND),
        ('Enchantment', Type.ENCHANTMENT),
        ('Enchantment - Aura', Type.ENCHANTMENT),
        ('Artifact Land', Type.LAND),
        ("Enchantment Land - Urza's Saga", Type.LAND),
        ('Artifact Land', Type.LAND),
        ('Land Creature - Forest Dryad', Type.LAND),
        ('Legendary Planeswalker - Jace', Type.PLANESWALKER),
        ('Instant - Arcane', Type.INSTANT),
        ('Legendary Sorcery', Type.SORCERY),
        ('Conspiracy', Type.UNKNOWN),
    ])
    def test_card_categorization(self, type_line, expected):
        card = Card(type_line=type_line)
        result = determine_category_from_card(card)
        self.assertEqual(expected, result)


class ColorPairTestCase(TestCase):

    @staticmethod
    @parameterized.expand([
        ('wu', {'W', 'U'}, ColorPair.WU),
        ('ub', {'U', 'B'}, ColorPair.UB),
        ('br', {'B', 'R'}, ColorPair.BR),
        ('rg', {'R', 'G'}, ColorPair.RG),
        ('gw', {'G', 'W'}, ColorPair.GW),
        ('wb', {'W', 'B'}, ColorPair.WB),
        ('bg', {'B', 'G'}, ColorPair.BG),
        ('gu', {'G', 'U'}, ColorPair.GU),
        ('ur', {'U', 'R'}, ColorPair.UR),
        ('rw', {'R', 'W'}, ColorPair.RW),
    ])
    def test_colorpair_from_set(self, _, colors, expected):
        self.assertEqual(expected, colorpair_from_set(colors))


class DeckImporterTestCase(TestCase):
    sample_commander_deck = [
        "C Norin, the Wary",
        "1 Lightning Bolt",
        "1 Mountain",
    ]

    def test_importing_commander_deck(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=norin,+the+wary',
                   create_mock_card_response('Norin, the Wary', '{R}', 'Legendary Creature - Coward'))
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=lightning+bolt',
                   create_mock_card_response('Lightning Bolt', '{R}', 'Instant'))
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=mountain',
                   create_mock_card_response('Mountain', '', 'Basic Land - Mountain'))
            process_decklist(self.sample_commander_deck)
        self.assertEqual(1, CommanderJumpstartDeck.objects.count())
        deck: CommanderJumpstartDeck = CommanderJumpstartDeck.objects.first()
        self.assertEqual(Color.RED, deck.color)
        norin = Card.objects.get(name='Norin, the Wary')
        self.assertEqual(deck.commander, norin)
        self.assertEqual(2, deck.cards.count())  # Note: Commanders aren't part of cards

    rograkh_decklist = [
        'C Rograkh, Son of Rohgahh',
        '39 Mountain',
    ]

    def test_rograkh_mana_cost_special_case(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=rograkh,+son+of+rohgahh',
                   create_mock_card_response('Rograkh, Son of Rohgahh', '{0}', 'Legendary Creature - Kobold'))
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=mountain',
                   create_mock_card_response('Mountain', '', 'Basic Land - Mountain'))
            process_decklist(self.rograkh_decklist)
        self.assertEqual(1, CommanderJumpstartDeck.objects.count())
        deck: CommanderJumpstartDeck = CommanderJumpstartDeck.objects.first()
        self.assertEqual(Color.RED, deck.color)

    two_color_list = [
        '1 Craterhoof Behemoth',
        '1 Ancestral Recall',
        '1 Trygon Predator',
    ]

    def test_two_color_deck(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=craterhoof+behemoth',
                   create_mock_card_response('Craterhoof Behemoth', '{5}{G}{G}{G}', 'Creature - Beast'))
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=ancestral+recall',
                   create_mock_card_response('Ancestral Recall', '{U}', 'Instant'))
            rm.add('GET', 'https://api.scryfall.com/cards/named?fuzzy=trygon+predator',
                   create_mock_card_response('Trygon Predator', '{1}{G}{U}', 'Creature - Beast'))
            process_decklist(self.two_color_list)
        self.assertEqual(1, DualColoredDeck.objects.count())
        deck: DualColoredDeck = DualColoredDeck.objects.first()
        self.assertEqual(ColorPair.GU, deck.colors)
        self.assertEqual(3, deck.cards.count())


class CommanderJumpstartViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        test_set = MagicSet.objects.create(id=uuid.uuid4(), code='test', name='Testing')

        akroma = Card.objects.create(id=uuid.uuid4(), name='Akroma', mana_cost='{W}', type_line='Legendary Creature')
        urza = Card.objects.create(id=uuid.uuid4(), name='Urza', mana_cost='{U}', type_line='Legendary Creature')
        geth = Card.objects.create(id=uuid.uuid4(), name='Geth', mana_cost='{B}', type_line='Legendary Creature')
        jeska = Card.objects.create(id=uuid.uuid4(), name='Jeska', mana_cost='{R}', type_line='Legendary Creature')
        kamahl = Card.objects.create(id=uuid.uuid4(), name='Kamahl', mana_cost='{G}', type_line='Legendary Creature')

        Printing.objects.bulk_create([
            Printing(magic_set=test_set, card=akroma, image_url='https://example.com/akroma.png'),
            Printing(magic_set=test_set, card=urza, image_url='https://example.com/urza.png'),
            Printing(magic_set=test_set, card=geth, image_url='https://example.com/geth.png'),
            Printing(magic_set=test_set, card=jeska, image_url='https://example.com/jeska.png'),
            Printing(magic_set=test_set, card=kamahl, image_url='https://example.com/kamahl.png'),
        ])

        CommanderJumpstartDeck.objects.bulk_create([
            CommanderJumpstartDeck(color=Color.WHITE, commander=akroma, slug='akroma'),
            CommanderJumpstartDeck(color=Color.BLUE, commander=urza, slug='urza'),
            CommanderJumpstartDeck(color=Color.BLACK, commander=geth, slug='geth'),
            CommanderJumpstartDeck(color=Color.RED, commander=jeska, slug='jeska'),
            CommanderJumpstartDeck(color=Color.GREEN, commander=kamahl, slug='kamahl'),
        ])

    def test_first_selection_get(self):
        with patch('random.sample', side_effect=lambda a, b: a[:b]):
            response = self.client.get('/cmdrjump/')
        self.assertEqual(200, response.status_code)
        self.assertTrue('options' in response.context)
        self.assertEqual(3, len(response.context['options']))

        options = response.context['options']
        self.assertEqual('Akroma', options[0]['name'])
        self.assertEqual(Color.WHITE, options[0]['color'])
        self.assertEqual('akroma', options[0]['slug'])
        self.assertEqual('https://example.com/akroma.png', options[0]['image_url'])
        self.assertEqual('/cmdrjump/akroma?passed=2,3', options[0]['url'])

        self.assertEqual('Urza', options[1]['name'])
        self.assertEqual(Color.BLUE, options[1]['color'])
        self.assertEqual('urza', options[1]['slug'])
        self.assertEqual('https://example.com/urza.png', options[1]['image_url'])
        self.assertEqual('/cmdrjump/urza?passed=1,3', options[1]['url'])

        self.assertEqual('Geth', options[2]['name'])
        self.assertEqual(Color.BLACK, options[2]['color'])
        self.assertEqual('geth', options[2]['slug'])
        self.assertEqual('https://example.com/geth.png', options[2]['image_url'])
        self.assertEqual('/cmdrjump/geth?passed=1,2', options[2]['url'])

    def test_second_selection_with_passed(self):
        jace = Card.objects.create(id=uuid.uuid4(), name='Jace', mana_cost='{U}', type_line='Legendary Creature')
        yawg = Card.objects.create(id=uuid.uuid4(), name='Yawgmoth', mana_cost='{B}', type_line='Legendary Creature')

        test_set = MagicSet.objects.first()
        Printing.objects.bulk_create([
            Printing(magic_set=test_set, card=jace, image_url='https://example.com/jace.png'),
            Printing(magic_set=test_set, card=yawg, image_url='https://example.com/yawg.png'),
        ])

        CommanderJumpstartDeck.objects.bulk_create([
            CommanderJumpstartDeck(color=Color.BLUE, commander=jace, slug='jace'),
            CommanderJumpstartDeck(color=Color.BLACK, commander=yawg, slug='yawg'),
        ])

        with patch('random.sample', side_effect=lambda a, b: a[:b]):
            response = self.client.get('/cmdrjump/akroma?passed=2,3')
        self.assertEqual(200, response.status_code)
        self.assertTrue('options' in response.context)
        self.assertEqual(3, len(response.context['options']))

        options = response.context['options']
        self.assertFalse(2 in [item['id'] for item in options])
        self.assertFalse(3 in [item['id'] for item in options])

        self.assertEqual(['Jace', 'Yawgmoth', 'Jeska'], [item['name'] for item in options])

    def test_second_selection_without_passed(self):
        with patch('random.sample', side_effect=lambda a, b: a[:b]):
            response = self.client.get('/cmdrjump/urza')
        self.assertEqual(200, response.status_code)
        self.assertTrue('options' in response.context)
        self.assertEqual(3, len(response.context['options']))

        options = response.context['options']
        self.assertEqual(['Akroma', 'Geth', 'Jeska'], [item['name'] for item in options])

    def test_results(self):
        urza_deck = CommanderJumpstartDeck.objects.get(slug='urza')
        kamahl_deck = CommanderJumpstartDeck.objects.get(slug='kamahl')

        ch = Card.objects.create(id=uuid.uuid4(), name='Craterhoof Behemoth', type_line='Creature')
        ar = Card.objects.create(id=uuid.uuid4(), name='Ancestral Recall', type_line='Instant')
        tg = Card.objects.create(id=uuid.uuid4(), name='Trygon Predator', type_line='Artifact')

        CommanderJumpstartEntry.objects.bulk_create([
            CommanderJumpstartEntry(deck=urza_deck, card=ar, category=Type.INSTANT),
            CommanderJumpstartEntry(deck=kamahl_deck, card=ch, category=Type.CREATURE),
        ])

        gu = DualColoredDeck.objects.create(colors=ColorPair.GU)
        DualColoredEntry.objects.create(deck=gu, card=tg, category=Type.ARTIFACT)

        response = self.client.get('/cmdrjump/urza/kamahl')
        self.assertEqual(200, response.status_code)

        self.assertEqual(['Urza', 'Kamahl'], [item.name for item in response.context['commanders']])
        deck_sections = {
            'Creature': [
                {'count': 1, 'card': ch},
            ],
            'Artifact': [
                {'count': 1, 'card': tg},
            ],
            'Instant': [
                {'count': 1, 'card': ar},
            ],
        }
        self.assertDictEqual(deck_sections, response.context['deck_sections'])
