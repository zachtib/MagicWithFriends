from django.shortcuts import render

from app.decorators import debug_only
from cards.models import MagicSet


@debug_only
def set_detail(request, set_id):
    magic_set = MagicSet.objects \
        .prefetch_related('printings__card') \
        .get(id=set_id)
    message = magic_set.name
    for printing in magic_set.printings.all():
        message += f'\n{printing.card.name}'

    return render(request, 'message.html', {
        'message': message,
    })
