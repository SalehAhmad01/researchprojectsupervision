from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from accounts.mixins import StudentRequiredMixin
from notifications.services import notify_user
from .forms import DraftSubmissionForm
from .models import DraftSubmission


class DraftListView(LoginRequiredMixin, ListView):
    model = DraftSubmission
    template_name = 'drafts/draft_list.html'
    context_object_name = 'drafts'

    def get_queryset(self):
        queryset = DraftSubmission.objects.select_related('project', 'submitted_by', 'project__supervisor')
        user = self.request.user
        if user.is_student:
            return queryset.filter(project__student=user)
        if user.is_supervisor:
            return queryset.filter(project__supervisor=user)
        return queryset


class DraftDetailView(LoginRequiredMixin, DetailView):
    model = DraftSubmission
    template_name = 'drafts/draft_detail.html'
    context_object_name = 'draft'

    def get_queryset(self):
        return DraftSubmission.objects.select_related('project', 'submitted_by').prefetch_related('feedbacks')


class DraftUploadView(StudentRequiredMixin, CreateView):
    model = DraftSubmission
    form_class = DraftSubmissionForm
    template_name = 'drafts/draft_upload.html'
    success_url = reverse_lazy('drafts:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.submitted_by = self.request.user
        form.instance.version = form.instance.next_version()
        response = super().form_valid(form)
        supervisor = form.instance.project.supervisor
        if supervisor:
            notify_user(supervisor, 'New draft submitted', str(form.instance), url=form.instance.get_absolute_url())
        messages.success(self.request, 'Draft uploaded successfully with version tracking.')
        return response
