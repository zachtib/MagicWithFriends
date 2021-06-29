import json
from pathlib import Path

from dungeons.models import Dungeon, DungeonRoom, DungeonPathway

FILENAME = Path(__file__).resolve().parent / "dungeons.json"


def importdungeons():
    with open(FILENAME) as f:
        loaded_data = json.load(f)
    for dungeon_data in loaded_data:
        name = dungeon_data["name"]
        entrances = dungeon_data["entrances"]
        exits = dungeon_data["exits"]
        Dungeon.objects.filter(name__exact=name).delete()
        dungeon = Dungeon.objects.create(name=name, is_official=True)
        dungeon_rooms = {}
        pathways = []
        for index, room_data in dungeon_data["rooms"].items():
            created_room = DungeonRoom.objects.create(
                dungeon=dungeon,
                name=room_data["name"],
                is_entrance=(index in entrances),
                is_exit=(index in exits),
                room_text=room_data["text"],
            )
            dungeon_rooms[index] = created_room
            for path in room_data["paths"]:
                pathways.append((index, path))
        for origin_index, destination_index in pathways:
            origin_room = dungeon_rooms[origin_index]
            destination_room = dungeon_rooms[destination_index]
            DungeonPathway.objects.create(
                origin=origin_room,
                destination=destination_room,
            )
