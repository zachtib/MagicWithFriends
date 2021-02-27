from django.conf import settings
from django.shortcuts import redirect, render, resolve_url


def inspectable_redirect(request, to):
    if settings.DEBUG:
        return render(request, 'redirect_link.html', {
            'url': resolve_url(to)
        })
    return redirect(to)
