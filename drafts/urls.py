from django.urls import path, include

from . import views

urlpatterns = [
    path('mine', views.my_drafts, name='my-drafts'),
    path('<uuid:draft_id>/', include([
        path('join', views.draft_join, name='join-draft'),
        path('', views.draft_detail, name='draft-detail'),
    ])),
]