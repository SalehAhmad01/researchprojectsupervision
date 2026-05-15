from django.test import TestCase

from accounts.models import User
from .services import notify_user


class NotificationTests(TestCase):
    def test_notify_user_creates_notification(self):
        user = User.objects.create_user(username='student', password='StrongPass123')
        notification = notify_user(user, 'Title', 'Message')
        self.assertEqual(notification.recipient, user)
