from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        INFO = 'info', 'Information'
        APPROVAL = 'approval', 'Approval'
        FEEDBACK = 'feedback', 'Feedback'
        DEADLINE = 'deadline', 'Deadline'
        WARNING = 'warning', 'Warning'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=160)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=Type.choices, default=Type.INFO)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read', '-created_at'])]

    def __str__(self):
        return self.title
