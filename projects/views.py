from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import CoordinatorRequiredMixin, StudentRequiredMixin
from accounts.models import User
from notifications.services import notify_user
from .forms import ResearchProjectForm, SupervisorAssignmentForm
from .models import ResearchProject, SupervisorAssignment
from .services import supervisor_has_conflict


class ProjectListView(LoginRequiredMixin, ListView):
    model = ResearchProject
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = ResearchProject.objects.select_related('student', 'supervisor', 'coordinator')
        user = self.request.user
        if user.is_student:
            return queryset.filter(student=user)
        if user.is_supervisor:
            return queryset.filter(supervisor=user)
        return queryset


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = ResearchProject
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return ResearchProject.objects.select_related('student', 'supervisor', 'coordinator').prefetch_related('drafts')


class ProjectCreateView(StudentRequiredMixin, CreateView):
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:list')

    def form_valid(self, form):
        form.instance.student = self.request.user
        messages.success(self.request, 'Research topic submitted for coordinator review.')
        return super().form_valid(form)


class SupervisorAssignmentView(CoordinatorRequiredMixin, UpdateView):
    model = SupervisorAssignment
    form_class = SupervisorAssignmentForm
    template_name = 'projects/supervisor_assignment.html'
    success_url = reverse_lazy('projects:list')

    def get_object(self):
        project = get_object_or_404(ResearchProject, pk=self.kwargs['pk'])
        if hasattr(project, 'assignment'):
            return project.assignment
        supervisor = project.supervisor or User.objects.filter(role=User.Roles.SUPERVISOR, is_active=True).first()
        return SupervisorAssignment(project=project, supervisor=supervisor, assigned_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        return context

    def form_valid(self, form):
        assignment = form.save(commit=False)
        assignment.assigned_by = self.request.user
        if supervisor_has_conflict(assignment.supervisor, assignment.project.student):
            messages.warning(self.request, 'Potential department conflict detected for this assignment.')
        assignment.project.supervisor = assignment.supervisor
        assignment.project.status = ResearchProject.Status.UNDER_REVIEW
        assignment.project.save(update_fields=['supervisor', 'status', 'updated_at'])
        notify_user(assignment.supervisor, 'New supervision assignment', assignment.project.title, url=assignment.project.get_absolute_url())
        messages.success(self.request, 'Supervisor assigned successfully.')
        return super().form_valid(form)


class ProjectApproveView(CoordinatorRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(ResearchProject, pk=pk)
        project.approve(request.user)
        notify_user(project.student, 'Topic approved', project.title, url=project.get_absolute_url())
        messages.success(request, 'Project approved successfully.')
        return redirect(project)
