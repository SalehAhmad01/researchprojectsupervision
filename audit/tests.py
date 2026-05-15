from django.test import TestCase

from .models import ActivityLog


class ActivityLogTests(TestCase):
    def test_activity_log_string(self):
        log = ActivityLog.objects.create(action='test')
        self.assertIn('test', str(log))
