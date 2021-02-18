from django.conf import settings


def debug_only(func):
    def raise_404():
        from django.http import Http404
        raise Http404()

    if settings.DEBUG:
        return func
    return raise_404
