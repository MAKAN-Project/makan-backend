from .models import Notification

def create_notification(recipient, message, notif_type='system', sender=None, project_request=None, session=None):
    """
    إنشاء إشعار جديد في النظام بطريقة موحدة.
    """
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=notif_type,
        message=message,
        project_request=project_request,
        session=session
    )
