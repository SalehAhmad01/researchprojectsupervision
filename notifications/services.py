from .models import Notification


def notify_user(recipient, title, message, notification_type=Notification.Type.INFO, url=''):
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        url=url,
    )
