from django.urls import path

from .views import CoordinatorDashboardView, DashboardRedirectView, StudentDashboardView, SupervisorDashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardRedirectView.as_view(), name='index'),
    path('student/', StudentDashboardView.as_view(), name='student'),
    path('supervisor/', SupervisorDashboardView.as_view(), name='supervisor'),
    path('coordinator/', CoordinatorDashboardView.as_view(), name='coordinator'),
]
