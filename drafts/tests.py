from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounts.models import User
from projects.models import ResearchProject
from .models import DraftSubmission


class DraftSubmissionTests(TestCase):
    def test_draft_versioning_preserves_versions(self):
        student = User.objects.create_user(username='student', password='StrongPass123')
        project = ResearchProject.objects.create(student=student, title='Secure Research System', abstract='Research abstract', status=ResearchProject.Status.APPROVED)
        file_one = SimpleUploadedFile('chapter1.pdf', b'file-one', content_type='application/pdf')
        file_two = SimpleUploadedFile('chapter1.pdf', b'file-two', content_type='application/pdf')
        first = DraftSubmission.objects.create(project=project, chapter=1, version=1, file=file_one, submitted_by=student)
        second = DraftSubmission.objects.create(project=project, chapter=1, version=2, file=file_two, submitted_by=student)
        self.assertEqual(first.version, 1)
        self.assertEqual(second.version, 2)
