from django.urls import path, include

from . import views

urlpatterns = [
    path('<uuid:cube_id>/', include([
        path('bulk-update', views.cube_bulk_update, name='cube-bulk-update'),
        path('create-draft', views.cube_create_draft, name='cube-create-draft'),
        path('', views.cube_detail, name='cube-detail'),
    ])),
]
