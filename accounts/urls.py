from django.urls import path

from .views import ProfileView, RegisterView, UserLoginView, UserLogoutView, UserManagementView

app_name = 'accounts'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('manage-users/', UserManagementView.as_view(), name='user_management'),
]
