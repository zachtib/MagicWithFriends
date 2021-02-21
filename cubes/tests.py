from django.contrib.auth.models import User
from django.test import TestCase

from cubes.models import Cube

sample_data = """Command Beacon
Ojutai's Command
Silumgar's Command
Atarka's Command
Kolaghan's Command
Dromoka's Command
Dragonlord Atarka
Dragonlord Dromoka
Dragonlord Kolaghan
Dragonlord Ojutai
Dragonlord Silumgar
Austere Command
Cryptic Command
Incendiary Command
Primal Command
Profane Command
Arcades, the Strategist
Vaevictis Asmadi, the Dire
Nicol Bolas, the Ravager
Palladia-Mors, the Ruiner
Chromium, the Mutable
Anara, Wolvid Familiar
Esior, Wardwing Familiar
Falthis, Shadowcat Familiar
Kediss, Emberclaw Familiar
Keleth, Sunmane Familiar
Brutal Hordechief
Shaman of the Great Hunt
Soulfire Grand Master
Torrent Elemental
Warden of the First Tree
Alesha, Who Smiles at Death
Atarka, World Render
Daghatar the Adamant
Dromoka, the Eternal
Kolaghan, the Storm's Fury
Ojutai, Soul of Winter
Shu Yun, the Silent Tempest
Silumgar, the Drifting Death
Tasigur, the Golden Fang
Yasova Dragonclaw
The Ur-Dragon
Sylvan Library
Crux of Fate
Mystic Confluence
Wretched Confluence
Fiery Confluence
Verdant Confluence
Righteous Confluence
Collective Defiance
Collective Brutality
Collective Effort
Crush Contraband
Cleansing Nova
Heliod's Intervention
Thassa's Intervention
Erebos's Intervention
Purphoros's Intervention
Nylea's Intervention
Archmage's Charm
Charming Prince
Opt
Swords to Plowshares
Demonic Tutor
Lorehold Command
Witherbloom Command
Silverquill Command
Quandrix Command
Prismari Command""".splitlines()


class CubeTestCase(TestCase):

    def setUp(self) -> None:
        self.owner = User.objects.create_user("cubeowner")
        self.cube = Cube.objects.create(name='Test Cube', owner=self.owner)

    def test_bulk_update(self):
        self.cube.bulk_update(sample_data)
        self.assertEqual(len(sample_data), self.cube.entries.count())

    def test_size(self):
        self.cube.bulk_update(sample_data)
        self.assertEqual(len(sample_data), self.cube.calculate_size())

    def test_pack_generation(self):
        self.cube.bulk_update(sample_data)
        packs = self.cube.generate_packs()
        self.assertIsNotNone(packs)
