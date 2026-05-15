from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RoleAuthenticationForm(AuthenticationForm):
    role = forms.ChoiceField(choices=User.Roles.choices, widget=forms.HiddenInput)

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        selected_role = self.cleaned_data.get('role')
        if selected_role == User.Roles.COORDINATOR:
            if not user.is_coordinator:
                raise forms.ValidationError('Please use the correct login option for your account role.', code='invalid_role')
            return
        if user.role != selected_role:
            raise forms.ValidationError('Please use the correct login option for your account role.', code='invalid_role')


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'student_id', 'staff_id', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        student_id = cleaned_data.get('student_id')
        staff_id = cleaned_data.get('staff_id')
        if role == User.Roles.STUDENT:
            cleaned_data['staff_id'] = None
            if not student_id:
                self.add_error('student_id', 'Student ID is required for student accounts.')
        elif role in {User.Roles.SUPERVISOR, User.Roles.COORDINATOR}:
            cleaned_data['student_id'] = None
            if not staff_id:
                self.add_error('staff_id', 'Staff ID is required for supervisor and coordinator accounts.')
        return cleaned_data


class BulkUserUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV file',
        help_text='Required columns: username, email, role. Optional columns: first_name, last_name, department, student_id, staff_id, phone, password, eligible.',
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.lower().endswith('.csv'):
            raise forms.ValidationError('Please upload a CSV file.')
        if csv_file.size > 2 * 1024 * 1024:
            raise forms.ValidationError('CSV file must not exceed 2MB.')
        return csv_file


class BulkAssignmentUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Assignment CSV file',
        help_text='Required columns: student_username, supervisor_username. Optional columns: project_title, notes.',
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.lower().endswith('.csv'):
            raise forms.ValidationError('Please upload a CSV file.')
        if csv_file.size > 2 * 1024 * 1024:
            raise forms.ValidationError('CSV file must not exceed 2MB.')
        return csv_file


class SingleUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text='Leave blank to create the account without a usable password.')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'student_id', 'staff_id', 'phone', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (User.Roles.STUDENT, 'Student'),
            (User.Roles.SUPERVISOR, 'Supervisor'),
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        student_id = cleaned_data.get('student_id')
        staff_id = cleaned_data.get('staff_id')
        if role == User.Roles.STUDENT:
            cleaned_data['staff_id'] = None
            if not student_id:
                self.add_error('student_id', 'Student ID is required for student accounts.')
        elif role == User.Roles.SUPERVISOR:
            cleaned_data['student_id'] = None
            if not staff_id:
                self.add_error('staff_id', 'Staff ID is required for supervisor accounts.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if user.role == User.Roles.STUDENT:
            user.staff_id = None
        elif user.role == User.Roles.SUPERVISOR:
            user.student_id = None
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'department', 'student_id', 'staff_id', 'phone']
