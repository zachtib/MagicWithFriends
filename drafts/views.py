import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, reverse

from .models import Draft, DraftEntry, DraftSeat


@login_required
def my_drafts(request):
    entries = DraftEntry.objects.filter(player=request.user)
    seats = DraftSeat.objects.filter(user=request.user)

    response = ['My Drafts:']
    for entry in entries:
        response.append(f'Entry in {entry.draft}')
    for seat in seats:
        response.append(f'Seat #{seat.position} of {seat.draft}')
    return HttpResponse('\n'.join(response))


@login_required
def draft_detail(request, draft_id: uuid):
    draft = get_object_or_404(Draft, uuid=draft_id)
    is_owner = draft.creator.id == request.user.id
    in_draft = not request.user.is_anonymous and draft.is_user_in_draft(request.user)
    join_url = reverse('join-draft', args=[draft.uuid])

    if not draft.is_started:
        return render(request, 'drafts/detail.html', {
            'is_owner': is_owner,
            'join_url': join_url,
            'draft': draft,
        })
    else:
        if not in_draft:
            return render(request, 'drafts/detail.html', {
                'is_owner': is_owner,
                'join_url': join_url,
                'draft': draft,
            })
        seat = draft.get_seat_for_user(request.user)
        current_pack = seat.get_current_pack()
        pack_count = seat.get_pack_count()
        return render(request, 'drafts/pick.html', {
            'draft': draft,
            'pack': current_pack,
            'pack_count': pack_count,
            'picks': seat.picks
        })


@login_required
def draft_join(request, draft_id: uuid):
    draft = get_object_or_404(Draft, uuid=draft_id)
    join_success = draft.join(request.user)
    if join_success:
        return HttpResponse('OK')
    else:
        return HttpResponse('Error')


@login_required
def draft_leave(request, draft_id: uuid):
    return render(request, '')
