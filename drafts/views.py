import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, reverse, redirect

from core.http import inspectable_redirect
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
    show_start_button = is_owner and draft.entries.count() > 0

    if not draft.is_started:
        return render(request, 'drafts/detail.html', {
            'is_owner': is_owner,
            'in_draft': in_draft,
            'join_url': join_url,
            'show_start_button': show_start_button,
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
        is_complete = draft.current_round > 3
        seats = [seat.short_display_name() for seat in draft.seats.order_by('position')]
        return render(request, 'drafts/pick.html', {
            'draft': draft,
            'pack': current_pack,
            'pack_count': pack_count,
            'picks': seat.picks,
            'total_rounds': 3,
            'is_complete': is_complete,
            'seats': seats,
        })


@login_required
def draft_join(request, draft_id: uuid):
    draft = get_object_or_404(Draft, uuid=draft_id)
    join_success = draft.join(request.user)
    if join_success:
        return redirect(draft)
    else:
        return HttpResponse('Error')


@login_required
def draft_leave(request, draft_id: uuid):
    draft = get_object_or_404(Draft, uuid=draft_id)
    draft.entries.filter(player=request.user).delete()
    return redirect(draft)


@login_required
def draft_start(request, draft_id: uuid):
    draft = get_object_or_404(Draft, uuid=draft_id)
    if draft.creator.id != request.user.id:
        return redirect(draft)
    draft.begin()
    return redirect(draft)


@login_required
def draft_pick(request, draft_id, card_id):
    draft = get_object_or_404(Draft, uuid=draft_id)
    seat = draft.get_seat_for_user(request.user)
    if seat.make_selection(card_id):
        draft.heartbeat()
    return inspectable_redirect(request, draft)
