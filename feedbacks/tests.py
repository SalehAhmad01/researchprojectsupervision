from django.test import TestCase

from .forms import FeedbackForm


class FeedbackFormTests(TestCase):
    def test_progress_score_cannot_exceed_100(self):
        form = FeedbackForm(data={'decision': 'approved', 'comments': 'Good work', 'progress_score': 101})
        self.assertFalse(form.is_valid())
