from typing import List

from django.db import models
from django.utils.text import slugify


class Dungeon(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    is_official = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.name

    def entrances(self) -> List["DungeonRoom"]:
        return list(self.rooms.filter(is_entrance=True))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug != "":
            super().save(force_insert, force_update, using, update_fields)
            return
        slug = slugify(self.name)
        matching_slugs = Dungeon.objects.filter(slug__startswith=slug).values_list("slug", flat=True)

        if len(matching_slugs) == 0:
            self.slug = slug
            super().save(force_insert, force_update, using, update_fields)
            return

        index = 1
        for matching_slug in matching_slugs:
            suffix = matching_slug.rsplit("-", maxsplit=1)[1]
            try:
                int_suffix = int(suffix)
                if int_suffix >= index:
                    index = int_suffix + 1
            except ValueError as e:
                continue
        self.slug = f"{slug}-{index}"
        super().save(force_insert, force_update, using, update_fields)


class DungeonRoom(models.Model):
    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250)
    is_entrance = models.BooleanField(default=False)
    is_exit = models.BooleanField(default=False)
    room_text = models.TextField()

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None or self.slug == "":
            self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        unique_together = [
            ("dungeon", "name"),
            ("dungeon", "slug"),
        ]


class DungeonPathway(models.Model):
    origin = models.ForeignKey(DungeonRoom, on_delete=models.CASCADE, related_name="paths")
    destination = models.ForeignKey(DungeonRoom, on_delete=models.CASCADE, related_name="+")
