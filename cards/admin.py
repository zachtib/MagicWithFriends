from django import forms
from django.contrib import admin

from .models import *


class PrintingFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PrintingFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.prefetch_related("magic_set__printings")


class PrintingInline(admin.TabularInline):
    model = MagicSet.cards.through
    extra = 0
    formset = PrintingFormSet


class FaceInline(admin.StackedInline):
    model = CardFace
    extra = 0


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    inlines = [
        FaceInline,
        PrintingInline,
    ]


@admin.register(MagicSet)
class MagicSetAdmin(admin.ModelAdmin):
    inlines = [
        PrintingInline,
    ]

    exclude = ('printings',)
    #
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.prefetch_related('printings')
    #     return queryset
    #
    # def get_object(self, request, object_id, from_field=None):
    #     try:
    #         return MagicSet.objects\
    #             .prefetch_related(
    #                 Prefetch('printings')
    #             )\
    #             .get(id=object_id)
    #
    #     except MagicSet.DoesNotExist:
    #         return None
