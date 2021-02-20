from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from drafts.models import Draft
from .models import Cube


def cube_detail(request, cube_id):
    cube = get_object_or_404(Cube, id=cube_id)
    show_draft_button = not request.user.is_anonymous
    draft_url = reverse('cube-create-draft', args=[cube.id])
    return render(request, 'cubes/detail.html', {
        'cube': cube,
        'show_draft_button': show_draft_button,
        'draft_url': draft_url,
    })


def cube_create_draft(request, cube_id):
    cube = get_object_or_404(Cube, id=cube_id)
    new_draft = Draft.objects.create(
        name=f'Draft of {cube.name}',
        creator=request.user,
        cube=cube,
    )
    return redirect(new_draft)


def cube_bulk_update(request, cube_id):
    pass
