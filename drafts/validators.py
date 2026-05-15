import os

from django.core.exceptions import ValidationError


ALLOWED_DRAFT_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_DRAFT_SIZE = 5 * 1024 * 1024


def validate_draft_file(file):
    extension = os.path.splitext(file.name)[1].lower()
    if extension not in ALLOWED_DRAFT_EXTENSIONS:
        raise ValidationError('Only PDF, DOC, and DOCX files are allowed.')
    if file.size > MAX_DRAFT_SIZE:
        raise ValidationError('Draft file size must not exceed 5MB.')
