from django.test import TestCase

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
