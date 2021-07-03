from dataclasses import dataclass

from django.urls import reverse


@dataclass
class ToolbarItem:
    label: str
    is_active: bool
    url: str


def toolbar(request):
    def create_item(label, view_name):
        url = reverse(view_name)
        return ToolbarItem(label=label, is_active=request.path.startswith(url), url=url)

    return {
        "toolbar_items": [
            create_item("Commander JumpStart", "cj-begin"),
            create_item("Dungeons", "dungeon-list"),
        ],
    }
