from django.conf import settings
from django.db import models


class Feedback(models.Model):
    class Decision(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        REVISION_REQUIRED = 'revision_required', 'Revision Required'

    draft = models.ForeignKey('drafts.DraftSubmission', on_delete=models.CASCADE, related_name='feedbacks')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='feedbacks_given')
    decision = models.CharField(max_length=30, choices=Decision.choices, db_index=True)
    comments = models.TextField()
    progress_score = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['draft', '-created_at'])]

    def __str__(self):
        return f'{self.draft} - {self.get_decision_display()}'
