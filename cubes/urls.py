from django.urls import path, include

from . import views

urlpatterns = [
    path('<uuid:cube_id>/', include([
        path('bulk-update', views.cube_bulk_update, name='cube-bulk-update'),
        path('create-draft', views.cube_create_draft, name='cube-create-draft'),
        path('', views.cube_detail, name='cube-detail'),
    ])),
    path('untap/<str:cube_id>', views.cobra_untap_export),
    path('inspect/', views.cube_inspection, name='inspect-cube'),
    path('inspect/<str:cube_id>', views.cobra_set_inspection, name='inspect-cube-results'),
    path('inspect/<str:cube_id>/<str:set_id>', views.cobra_set_inspection, name='inspect-cube-set'),
    path('', views.cube_list, name='cube-list'),
]
