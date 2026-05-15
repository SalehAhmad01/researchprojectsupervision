from django.urls import path

from .views import ProjectApproveView, ProjectCreateView, ProjectDetailView, ProjectListView, SupervisorAssignmentView

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='list'),
    path('submit/', ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/assign-supervisor/', SupervisorAssignmentView.as_view(), name='assign_supervisor'),
    path('<int:pk>/approve/', ProjectApproveView.as_view(), name='approve'),
]
