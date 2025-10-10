from users.models import User
from notifications.models import Notification

def notifications_context(request):
    user = None

    # ✅ استخدم فقط session لأن نظامك مش مبني على Django Auth
    if request.session.get('user_id'):
        try:
            user = User.objects.get(user_id=request.session['user_id'])
        except User.DoesNotExist:
            user = None

    if isinstance(user, User):
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).order_by('-created_at')[:5]

        all_notifications = Notification.objects.filter(
            recipient=user
        ).order_by('-created_at')

        return {
            'pending_notifications': pending_notifications,
            'all_notifications': all_notifications,
        }

    # 🔹 إذا ما في مستخدم → نرجع قوام فارغة
    return {
        'pending_notifications': [],
        'all_notifications': [],
    }
