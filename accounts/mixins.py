from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied('You do not have permission to access this page.')
        return super().handle_no_permission()


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['student']


class SupervisorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['supervisor']


class CoordinatorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['coordinator']

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_coordinator
