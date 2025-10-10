from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

# ✅ عرض كل الإشعارات الخاصة بالمستخدم الحالي
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(recipient=user).order_by('-created_at')


# ✅ تعليم إشعار كمقروء
class MarkAsReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def update(self, request, *args, **kwargs):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'detail': 'Notification marked as read'}, status=status.HTTP_200_OK)
