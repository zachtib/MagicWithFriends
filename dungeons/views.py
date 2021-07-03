from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from dungeons.models import Dungeon, DungeonRoom

COMPLETED_DUNGEONS = "completed_dungeons"


def dungeon_list(request):
    completed_dungeon_ids = request.session.get(COMPLETED_DUNGEONS, [])
    completed_dungeons = Dungeon.objects.filter(id__in=completed_dungeon_ids)
    official_dungeons = Dungeon.objects.filter(is_official=True).exclude(id__in=completed_dungeon_ids)
    remaining_dungeons = Dungeon.objects.filter(is_official=False).exclude(id__in=completed_dungeon_ids)

    paginator = Paginator(remaining_dungeons, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'dungeons/list.html', {
        'completed_dungeons': completed_dungeons,
        'official_dungeons': official_dungeons,
        'dungeons': page,
        'completed_ids': completed_dungeon_ids,
    })


def dungeon_entrance(request, dungeon_slug):
    dungeon = get_object_or_404(Dungeon, slug=dungeon_slug)

    return render(request, 'dungeons/choice.html', {
        'title': dungeon.name,
        'text': 'Enter the Dungeon',
        'choices': {room.name: room.get_absolute_url() for room in dungeon.entrances()},
    })


def dungeon_room(request, dungeon_slug, room_slug):
    dungeon = get_object_or_404(Dungeon, slug=dungeon_slug)
    room = get_object_or_404(DungeonRoom, slug=room_slug, dungeon=dungeon)

    if room.paths.count() > 0:
        destinations = [path.destination for path in room.paths.all()]
        choices = [
            dict(
                title=room.name,
                text=room.room_text,
                url=room.get_absolute_url()
            ) for room in destinations
        ]
    else:
        completed_dungeon_ids: list = request.session.get(COMPLETED_DUNGEONS, [])
        completed_dungeon_ids.append(dungeon.id)
        request.session[COMPLETED_DUNGEONS] = completed_dungeon_ids
        choices = [dict(title="End of the Dungeon", text="Return to Dungeon List", url=reverse("dungeon-list"))]

    return render(request, 'dungeons/room.html', {
        'dungeon': dungeon.name,
        'title': room.name,
        'text': room.room_text,
        'choices': choices,
    })


def clear_completed(request):
    request.session[COMPLETED_DUNGEONS] = []
    return HttpResponseRedirect(reverse("dungeon-list"))
