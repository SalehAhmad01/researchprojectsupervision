from django.test import TestCase
from accounts.models import User
from .models import ResearchProject
from .services import find_similar_topics


class ResearchProjectTests(TestCase):
    def test_duplicate_topic_detection_finds_similar_title(self):
        student = User.objects.create_user(username='student', password='StrongPass123')
        ResearchProject.objects.create(student=student, title='Machine Learning for Crop Disease Detection', abstract='Research abstract')
        self.assertTrue(find_similar_topics('Crop Disease Detection Using Machine Learning').exists())

