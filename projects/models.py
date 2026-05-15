from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class ResearchProject(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        UNDER_REVIEW = 'under_review', 'Under Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        COMPLETED = 'completed', 'Completed'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_projects')
    title = models.CharField(max_length=255, db_index=True)
    abstract = models.TextField()
    keywords = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.SUBMITTED, db_index=True)
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_projects')
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinated_projects')
    approval_date = models.DateTimeField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['supervisor', 'status']),
        ]

    def __str__(self):
        return self.title

    def approve(self, coordinator):
        self.status = self.Status.APPROVED
        self.coordinator = coordinator
        self.approval_date = timezone.now()
        self.save(update_fields=['status', 'coordinator', 'approval_date', 'updated_at'])

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'pk': self.pk})


class SupervisorAssignment(models.Model):
    project = models.OneToOneField(ResearchProject, on_delete=models.CASCADE, related_name='assignment')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='project_assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='supervisor_assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.project} -> {self.supervisor}'
