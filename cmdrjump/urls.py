from django.urls import path

from . import views

urlpatterns = [
    path('', views.start, name='cj-begin'),
    path('<str:cmdr>', views.make_second_selection, name='cj-second-selection'),
    path('<str:cmdr_1>/<str:cmdr_2>', views.result, name='cj-result'),
]
