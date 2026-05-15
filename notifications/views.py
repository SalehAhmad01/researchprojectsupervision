from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
        return redirect('notifications:list')
