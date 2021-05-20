from django.contrib import admin

from .models import *


class CommanderJumpstartEntryInline(admin.TabularInline):
    model = CommanderJumpstartEntry
    extra = 0


@admin.register(CommanderJumpstartDeck)
class CommanderJumpstartDeckAdmin(admin.ModelAdmin):
    inlines = [
        CommanderJumpstartEntryInline,
    ]


class DualColoredEntryInline(admin.TabularInline):
    model = DualColoredEntry
    extra = 0


@admin.register(DualColoredDeck)
class DualColoredDeckAdmin(admin.ModelAdmin):
    inlines = [
        DualColoredEntryInline,
    ]
