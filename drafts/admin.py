from django.contrib import admin
from .models import Draft


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    pass
