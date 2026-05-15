import csv
import io

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, UpdateView

from projects.models import ResearchProject, SupervisorAssignment
from .forms import BulkAssignmentUploadForm, BulkUserUploadForm, ProfileForm, RoleAuthenticationForm, SingleUserCreateForm, UserRegistrationForm
from .mixins import CoordinatorRequiredMixin
from .models import User


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = RoleAuthenticationForm

    def get_initial(self):
        initial = super().get_initial()
        initial['role'] = self.request.GET.get('role', User.Roles.STUDENT)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_role = self.request.POST.get('role') or self.request.GET.get('role') or User.Roles.STUDENT
        context['selected_role'] = selected_role
        context['role_options'] = [
            {'value': User.Roles.STUDENT, 'label': 'Student', 'description': 'Submit topics and upload chapter drafts.'},
            {'value': User.Roles.SUPERVISOR, 'label': 'Supervisor', 'description': 'Review drafts and provide feedback.'},
            {'value': User.Roles.COORDINATOR, 'label': 'Coordinator', 'description': 'Assign supervisors and monitor progress.'},
        ]
        return context


class UserLogoutView(LogoutView):
    pass


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        messages.success(self.request, 'Account created successfully. You can now sign in.')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


class UserManagementView(CoordinatorRequiredMixin, FormView):
    template_name = 'accounts/user_management.html'
    form_class = BulkUserUploadForm
    success_url = reverse_lazy('accounts:user_management')

    required_columns = {'username', 'email', 'role'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('single_user_form', SingleUserCreateForm())
        context.setdefault('assignment_form', BulkAssignmentUploadForm())
        context['students'] = User.objects.filter(role=User.Roles.STUDENT).order_by('username')
        context['supervisors'] = User.objects.filter(role=User.Roles.SUPERVISOR).order_by('username')
        context['eligible_students'] = User.objects.filter(role=User.Roles.STUDENT, is_verified=True).count()
        context['active_tab'] = getattr(self, 'active_tab', 'bulk')
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'single_user':
            self.active_tab = 'single'
            single_user_form = SingleUserCreateForm(request.POST)
            if single_user_form.is_valid():
                user = single_user_form.save()
                messages.success(request, f'{user.get_role_display()} account created for {user.username}.')
                return super().form_valid(single_user_form)
            bulk_form = self.get_form()
            return self.render_to_response(self.get_context_data(form=bulk_form, single_user_form=single_user_form))
        if request.POST.get('action') == 'bulk_assign':
            self.active_tab = 'assign'
            assignment_form = BulkAssignmentUploadForm(request.POST, request.FILES)
            if assignment_form.is_valid():
                return self.process_bulk_assignments(assignment_form)
            bulk_form = self.get_form()
            return self.render_to_response(self.get_context_data(form=bulk_form, assignment_form=assignment_form))
        self.active_tab = 'bulk'
        return super().post(request, *args, **kwargs)

    def parse_bool(self, value, default=False):
        if value is None or value == '':
            return default
        return str(value).strip().lower() in {'1', 'true', 'yes', 'y', 'eligible'}

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['csv_file']
        decoded_file = uploaded_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded_file))
        if not reader.fieldnames or not self.required_columns.issubset(set(reader.fieldnames)):
            form.add_error('csv_file', 'CSV must include username, email, and role columns.')
            return self.form_invalid(form)

        created_count = 0
        updated_count = 0
        skipped_rows = []
        allowed_roles = {User.Roles.STUDENT, User.Roles.SUPERVISOR}

        for row_number, row in enumerate(reader, start=2):
            username = (row.get('username') or '').strip()
            email = (row.get('email') or '').strip()
            role = (row.get('role') or '').strip().lower()
            if not username or not email or role not in allowed_roles:
                skipped_rows.append(row_number)
                continue

            defaults = {
                'email': email,
                'role': role,
                'first_name': (row.get('first_name') or '').strip(),
                'last_name': (row.get('last_name') or '').strip(),
                'department': (row.get('department') or '').strip(),
                'phone': (row.get('phone') or '').strip(),
                'student_id': (row.get('student_id') or '').strip() or None,
                'staff_id': (row.get('staff_id') or '').strip() or None,
                'is_active': True,
                'is_verified': self.parse_bool(row.get('eligible'), default=role == User.Roles.STUDENT),
            }
            if role == User.Roles.STUDENT:
                defaults['staff_id'] = None
            else:
                defaults['student_id'] = None

            user, created = User.objects.update_or_create(username=username, defaults=defaults)
            password = (row.get('password') or '').strip()
            if created:
                created_count += 1
                if password:
                    user.set_password(password)
                else:
                    user.set_unusable_password()
                user.save(update_fields=['password'])
            else:
                updated_count += 1
                if password:
                    user.set_password(password)
                    user.save(update_fields=['password'])

        messages.success(self.request, f'Bulk upload complete. Created {created_count}, updated {updated_count}.')
        if skipped_rows:
            messages.warning(self.request, f'Skipped invalid rows: {", ".join(map(str, skipped_rows))}.')
        return super().form_valid(form)

    def process_bulk_assignments(self, form):
        uploaded_file = form.cleaned_data['csv_file']
        decoded_file = uploaded_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded_file))
        required_columns = {'student_username', 'supervisor_username'}
        if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
            form.add_error('csv_file', 'CSV must include student_username and supervisor_username columns.')
            return self.render_to_response(self.get_context_data(form=self.get_form(), assignment_form=form))

        assigned_count = 0
        skipped_rows = []
        for row_number, row in enumerate(reader, start=2):
            student_username = (row.get('student_username') or '').strip()
            supervisor_username = (row.get('supervisor_username') or '').strip()
            project_title = (row.get('project_title') or '').strip()
            notes = (row.get('notes') or '').strip()
            student = User.objects.filter(username=student_username, role=User.Roles.STUDENT, is_verified=True).first()
            supervisor = User.objects.filter(username=supervisor_username, role=User.Roles.SUPERVISOR, is_active=True).first()
            if not student or not supervisor:
                skipped_rows.append(row_number)
                continue
            projects = ResearchProject.objects.filter(student=student)
            if project_title:
                projects = projects.filter(title__iexact=project_title)
            project = projects.order_by('-created_at').first()
            if not project:
                skipped_rows.append(row_number)
                continue
            assignment, _ = SupervisorAssignment.objects.update_or_create(
                project=project,
                defaults={'supervisor': supervisor, 'assigned_by': self.request.user, 'notes': notes},
            )
            project.supervisor = assignment.supervisor
            project.coordinator = self.request.user
            project.status = ResearchProject.Status.UNDER_REVIEW
            project.save(update_fields=['supervisor', 'coordinator', 'status', 'updated_at'])
            assigned_count += 1

        messages.success(self.request, f'Bulk assignment complete. Assigned {assigned_count} project(s).')
        if skipped_rows:
            messages.warning(self.request, f'Skipped rows with missing eligible student, supervisor, or project: {", ".join(map(str, skipped_rows))}.')
        return super().form_valid(form)
