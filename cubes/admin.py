from django.contrib import admin

from cubes.models import Cube


@admin.register(Cube)
class CubeAdmin(admin.ModelAdmin):
    pass
