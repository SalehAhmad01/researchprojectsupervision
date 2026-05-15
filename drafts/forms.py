from django import forms

from .models import DraftSubmission


class DraftSubmissionForm(forms.ModelForm):
    class Meta:
        model = DraftSubmission
        fields = ['project', 'chapter', 'file']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_student:
            self.fields['project'].queryset = user.student_projects.filter(status='approved')
