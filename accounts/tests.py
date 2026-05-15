from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from projects.models import ResearchProject, SupervisorAssignment
from .models import User


class UserModelTests(TestCase):
    def test_user_role_helpers(self):
        student = User.objects.create_user(username='student', password='StrongPass123', role=User.Roles.STUDENT)
        supervisor = User.objects.create_user(username='supervisor', password='StrongPass123', role=User.Roles.SUPERVISOR)
        coordinator = User.objects.create_user(username='coordinator', password='StrongPass123', role=User.Roles.COORDINATOR)
        self.assertTrue(student.is_student)
        self.assertTrue(supervisor.is_supervisor)
        self.assertTrue(coordinator.is_coordinator)

    def test_coordinator_can_bulk_upload_students_and_supervisors(self):
        coordinator = User.objects.create_user(username='coordinator2', password='StrongPass123', role=User.Roles.COORDINATOR)
        self.client.force_login(coordinator)
        csv_file = SimpleUploadedFile(
            'users.csv',
            b'username,email,role,first_name,last_name,department,student_id,staff_id,phone,password,eligible\nstudent3,student3@example.com,student,Test,Student,CS,S003,,0800,StrongPass123,true\nsupervisor3,supervisor3@example.com,supervisor,Test,Supervisor,CS,,F003,0900,StrongPass123,\n',
            content_type='text/csv',
        )
        response = self.client.post(reverse('accounts:user_management'), {'csv_file': csv_file}, HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='student3', role=User.Roles.STUDENT, student_id='S003', is_verified=True).exists())
        self.assertTrue(User.objects.filter(username='supervisor3', role=User.Roles.SUPERVISOR, staff_id='F003', department='CS').exists())

    def test_coordinator_can_create_single_user(self):
        coordinator = User.objects.create_user(username='coordinator3', password='StrongPass123', role=User.Roles.COORDINATOR)
        self.client.force_login(coordinator)
        response = self.client.post(reverse('accounts:user_management'), {
            'action': 'single_user',
            'username': 'single_student',
            'email': 'single@example.com',
            'first_name': 'Single',
            'last_name': 'Student',
            'role': User.Roles.STUDENT,
            'department': 'CS',
            'student_id': 'SS001',
            'phone': '0700',
            'password': 'StrongPass123',
        }, HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='single_student', role=User.Roles.STUDENT, student_id='SS001').exists())

    def test_coordinator_can_bulk_assign_eligible_students(self):
        coordinator = User.objects.create_user(username='coordinator4', password='StrongPass123', role=User.Roles.COORDINATOR)
        student = User.objects.create_user(username='eligible_student', password='StrongPass123', role=User.Roles.STUDENT, is_verified=True)
        supervisor = User.objects.create_user(username='department_supervisor', password='StrongPass123', role=User.Roles.SUPERVISOR, department='CS')
        project = ResearchProject.objects.create(student=student, title='Eligible Project', abstract='Research abstract')
        self.client.force_login(coordinator)
        csv_file = SimpleUploadedFile(
            'assignments.csv',
            b'student_username,supervisor_username,project_title,notes\neligible_student,department_supervisor,Eligible Project,Department match\n',
            content_type='text/csv',
        )
        response = self.client.post(reverse('accounts:user_management'), {'action': 'bulk_assign', 'csv_file': csv_file}, HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.supervisor, supervisor)
        self.assertEqual(project.coordinator, coordinator)
        self.assertTrue(SupervisorAssignment.objects.filter(project=project, supervisor=supervisor).exists())
