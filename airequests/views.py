from django.shortcuts import render

from django.shortcuts import get_object_or_404, redirect
from .models import AIRequest

def accept_request(request, request_id):
    ai_request = get_object_or_404(AIRequest, id=request_id)
    # هنا ممكن تحدّث حالة الطلب
    ai_request.status = 'accepted'
    ai_request.save()
    return redirect('engineer_dashboard')  # أو أي صفحة تريد إعادة التوجيه إليها
from django.shortcuts import get_object_or_404, redirect
from airequests.models import AIRequest

def reject_request(request, pk):
    ai_request = get_object_or_404(AIRequest, pk=pk)
    ai_request.status = "rejected"
    ai_request.save()
    return redirect('engineer_dashboard')  # أو أي صفحة بدك ترجع لها