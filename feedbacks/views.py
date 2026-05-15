from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from accounts.mixins import SupervisorRequiredMixin
from drafts.models import DraftSubmission
from notifications.services import notify_user
from .forms import FeedbackForm
from .models import Feedback


class FeedbackCreateView(SupervisorRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedbacks/feedback_form.html'
    success_url = reverse_lazy('drafts:list')

    def dispatch(self, request, *args, **kwargs):
        self.draft = get_object_or_404(DraftSubmission, pk=kwargs['draft_pk'], project__supervisor=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.draft = self.draft
        form.instance.supervisor = self.request.user
        self.draft.status = form.instance.decision
        self.draft.save(update_fields=['status'])
        notify_user(self.draft.project.student, 'Draft feedback received', str(self.draft), url=self.draft.get_absolute_url())
        messages.success(self.request, 'Feedback submitted successfully.')
        return super().form_valid(form)


class FeedbackHistoryView(SupervisorRequiredMixin, ListView):
    model = Feedback
    template_name = 'feedbacks/feedback_history.html'
    context_object_name = 'feedbacks'

    def get_queryset(self):
        return Feedback.objects.select_related('draft', 'draft__project', 'supervisor').filter(supervisor=self.request.user)
