from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import TemplateView

from drafts.models import DraftSubmission
from projects.models import ResearchProject


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_student:
            return redirect('dashboard:student')
        if request.user.is_supervisor:
            return redirect('dashboard:supervisor')
        return redirect('dashboard:coordinator')


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = ResearchProject.objects.filter(student=self.request.user).prefetch_related('drafts')
        context['project_progress'] = [
            {'project': project, 'progress': min(project.drafts.count() * 20, 100)}
            for project in projects
        ]
        return context


class SupervisorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/supervisor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = ResearchProject.objects.filter(supervisor=self.request.user)
        context['projects'] = projects
        context['pending_drafts'] = DraftSubmission.objects.filter(project__supervisor=self.request.user, status=DraftSubmission.Status.SUBMITTED)
        return context


class CoordinatorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/coordinator_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_projects'] = ResearchProject.objects.count()
        context['pending_approvals'] = ResearchProject.objects.filter(status=ResearchProject.Status.SUBMITTED).count()
        context['supervisor_workload'] = list(
            ResearchProject.objects.values('supervisor__username').annotate(total=Count('id')).order_by('-total')[:10]
        )
        context['project_status_counts'] = list(
            ResearchProject.objects.values('status').annotate(total=Count('id')).order_by('status')
        )
        context['delayed_submissions'] = ResearchProject.objects.filter(deadline__isnull=False, status__in=[ResearchProject.Status.SUBMITTED, ResearchProject.Status.UNDER_REVIEW]).count()
        return context
