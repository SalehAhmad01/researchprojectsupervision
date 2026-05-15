from django.urls import path

from .views import DraftDetailView, DraftListView, DraftUploadView

app_name = 'drafts'

urlpatterns = [
    path('', DraftListView.as_view(), name='list'),
    path('upload/', DraftUploadView.as_view(), name='upload'),
    path('<int:pk>/', DraftDetailView.as_view(), name='detail'),
]
