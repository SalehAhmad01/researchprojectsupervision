import hashlib
import os

from django.conf import settings
from django.db import models
from django.urls import reverse

from .validators import validate_draft_file


def draft_upload_path(instance, filename):
    base, extension = os.path.splitext(filename)
    return f'drafts/project_{instance.project_id}/chapter_{instance.chapter}/v{instance.version}{extension.lower()}'


class DraftSubmission(models.Model):
    class Chapter(models.IntegerChoices):
        CHAPTER_1 = 1, 'Chapter 1'
        CHAPTER_2 = 2, 'Chapter 2'
        CHAPTER_3 = 3, 'Chapter 3'
        CHAPTER_4 = 4, 'Chapter 4'
        CHAPTER_5 = 5, 'Chapter 5'

    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        REVISION_REQUIRED = 'revision_required', 'Revision Required'

    project = models.ForeignKey('projects.ResearchProject', on_delete=models.CASCADE, related_name='drafts')
    chapter = models.PositiveSmallIntegerField(choices=Chapter.choices, db_index=True)
    version = models.PositiveIntegerField(default=1)
    file = models.FileField(upload_to=draft_upload_path, validators=[validate_draft_file])
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.SUBMITTED, db_index=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='draft_submissions')
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-submitted_at']
        constraints = [
            models.UniqueConstraint(fields=['project', 'chapter', 'version'], name='unique_project_chapter_version'),
        ]
        indexes = [
            models.Index(fields=['project', 'chapter', '-version']),
            models.Index(fields=['status', 'submitted_at']),
        ]

    def __str__(self):
        return f'{self.project} - Chapter {self.chapter} v{self.version}'

    def save(self, *args, **kwargs):
        if not self.version:
            self.version = self.next_version()
        super().save(*args, **kwargs)
        if self.file and not self.file_hash:
            self.file_hash = self.calculate_hash()
            super().save(update_fields=['file_hash'])

    def next_version(self):
        latest = DraftSubmission.objects.filter(project=self.project, chapter=self.chapter).order_by('-version').first()
        return 1 if latest is None else latest.version + 1

    def calculate_hash(self):
        digest = hashlib.sha256()
        self.file.open('rb')
        for chunk in self.file.chunks():
            digest.update(chunk)
        self.file.close()
        return digest.hexdigest()

    def get_absolute_url(self):
        return reverse('drafts:detail', kwargs={'pk': self.pk})
