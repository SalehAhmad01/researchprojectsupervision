from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = 'student', 'Student'
        SUPERVISOR = 'supervisor', 'Supervisor'
        COORDINATOR = 'coordinator', 'Coordinator/Admin'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT, db_index=True)
    department = models.CharField(max_length=120, blank=True)
    student_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    staff_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_student(self):
        return self.role == self.Roles.STUDENT

    @property
    def is_supervisor(self):
        return self.role == self.Roles.SUPERVISOR

    @property
    def is_coordinator(self):
        return self.role == self.Roles.COORDINATOR or self.is_staff
