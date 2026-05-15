from django import forms

from accounts.models import User
from .models import ResearchProject, SupervisorAssignment
from .services import find_similar_topics


class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = ['title', 'abstract', 'keywords']

    def clean_title(self):
        title = self.cleaned_data['title']
        similar = find_similar_topics(title)
        if similar.exists():
            raise forms.ValidationError('A similar research topic already exists. Please revise your title.')
        return title


class SupervisorAssignmentForm(forms.ModelForm):
    supervisor = forms.ModelChoiceField(queryset=User.objects.filter(role=User.Roles.SUPERVISOR, is_active=True))

    class Meta:
        model = SupervisorAssignment
        fields = ['supervisor', 'notes']
