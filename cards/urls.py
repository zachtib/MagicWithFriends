from django.urls import path

from . import views

urlpatterns = [
    path('sets/<uuid:set_id>/', views.set_detail, name='set-detail'),
]
