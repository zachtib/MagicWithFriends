from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from drafts.models import Draft
from .forms import CubeBulkUpdateForm
from .models import Cube


def cube_list(request):
    cubes = Cube.objects.filter(owner=request.user)
    return render(request, 'cubes/list.html', {
        'cubes': cubes,
    })


def cube_detail(request, cube_id):
    queryset = Cube.objects.prefetch_related('entries', 'entries__printing', 'entries__printing__card')
    cube = get_object_or_404(queryset, id=cube_id)
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
        cube=cube
    )
    return redirect(new_draft)


def cube_bulk_update(request, cube_id):
    cube = get_object_or_404(Cube, id=cube_id)
    if request.method == 'POST':
        form = CubeBulkUpdateForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['bulk_content']
            lines = content.splitlines()
            cube.bulk_update(lines, fetch=True)
            return redirect(cube)
    else:
        form = CubeBulkUpdateForm()
    return render(request, 'cubes/update.html', {
        'cube': cube,
        'form': form,
    })
