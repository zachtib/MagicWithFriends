from django.shortcuts import render

from .models import CommanderJumpstartDeck


# Create your views here.
def start(request):
    choices = CommanderJumpstartDeck.objects.all().order_by('?')[:3]
    return render(request, 'message.html', {
        'message': ', '.join([choice.commander.name for choice in choices]),
    })


def second_selection(request, deck_id):
    pass


def result(request, cid_1, cid_2):
    pass
