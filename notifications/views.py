from rest_framework import generics, status
from rest_framework.response import Response
from .models import Notification
from users.models import User
from .serializers import NotificationSerializer
from django.http import JsonResponse
from django.shortcuts import render

# ✅ عرض كل الإشعارات الخاصة بالمستخدم الحالي (session-based)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        if not user_id:
            return Notification.objects.none()
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Notification.objects.none()
        return Notification.objects.filter(recipient=user).order_by('-created_at')


# ✅ تعليم إشعار كمقروء
class MarkAsReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def update(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        notif = self.get_object()
        if notif.recipient.user_id != user_id:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

        notif.is_read = True
        notif.save()
        return Response({'detail': 'Notification marked as read'}, status=status.HTTP_200_OK)


# ✅ عدد الإشعارات غير المقروءة
def unread_count(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({'count': 0})

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'count': 0})

    count = Notification.objects.filter(recipient=user, is_read=False).count()
    return JsonResponse({'count': count})


# ✅ صفحة عرض كل الإشعارات
def notifications_page(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'all_notifications.html', {'notifications': []})

    notifications = Notification.objects.filter(recipient_id=user_id).order_by('-created_at')
    return render(request, 'all_notifications.html', {'notifications': notifications})
