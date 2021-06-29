from django.test import TestCase

from dungeons.dungeonimporter import importdungeons
from dungeons.models import Dungeon


class DungeonTestCase(TestCase):

    def test_creating_dungeon_sets_slug(self):
        dungeon = Dungeon.objects.create(name="Tomb of Horrors")
        self.assertEqual("tomb-of-horrors", dungeon.slug)

    def test_attempted_collision_of_slug(self):
        dungeon1 = Dungeon.objects.create(name="Tomb of Horrors")
        self.assertEqual("tomb-of-horrors", dungeon1.slug)
        dungeon2 = Dungeon.objects.create(name="Tomb Of Horrors")
        self.assertNotEqual(dungeon1.slug, dungeon2.slug)
        self.assertEqual("tomb-of-horrors-1", dungeon2.slug)


class OfficialDungeonTestCase(TestCase):

    def setUp(self) -> None:
        importdungeons()

    def test_traversal(self):
        dungeon = Dungeon.objects.get(name="Dungeon of the Mad Mage")
        entrances = dungeon.entrances()

        self.assertEqual(1, len(entrances))

        room = entrances[0]
        paths = room.paths.all()

        self.assertEqual("Dungeon Level", paths[0].destination.name)
