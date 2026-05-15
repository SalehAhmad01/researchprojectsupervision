from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['decision', 'comments', 'progress_score']
        widgets = {'progress_score': forms.NumberInput(attrs={'min': 0, 'max': 100})}

    def clean_progress_score(self):
        score = self.cleaned_data['progress_score']
        if score > 100:
            raise forms.ValidationError('Progress score cannot exceed 100.')
        return score
