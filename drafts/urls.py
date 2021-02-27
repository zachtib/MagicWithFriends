from django.urls import path, include

from . import views

urlpatterns = [
    path('mine', views.my_drafts, name='my-drafts'),
    path('<uuid:draft_id>/', include([
        path('join', views.draft_join, name='join-draft'),
        path('leave', views.draft_leave, name='leave-draft'),
        path('start', views.draft_start, name='start-draft'),
        path('pick/<uuid:card_id>', views.draft_pick, name='draft-pick'),
        path('', views.draft_detail, name='draft-detail'),
    ])),
]
