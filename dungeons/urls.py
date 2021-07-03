from django.urls import path

from dungeons import views

urlpatterns = [
    path('reset', views.clear_completed, name='clear-completed'),
    path('venture/<str:dungeon_slug>/<str:room_slug>', views.dungeon_room, name='dungeon-room'),
    path('venture/<str:dungeon_slug>', views.dungeon_entrance, name='dungeon-entrance'),
    path('', views.dungeon_list, name='dungeon-list'),
]
