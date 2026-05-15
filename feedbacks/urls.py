from django.urls import path

from .views import FeedbackCreateView, FeedbackHistoryView

app_name = 'feedbacks'

urlpatterns = [
    path('history/', FeedbackHistoryView.as_view(), name='history'),
    path('draft/<int:draft_pk>/review/', FeedbackCreateView.as_view(), name='create'),
]
