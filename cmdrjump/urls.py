from django.urls import path

from . import views

urlpatterns = [
    path('', views.start),
    path('<int:deck_id>', views.second_selection),
    path('<int:cid_1>/<int:cid_2>', views.result),
]
