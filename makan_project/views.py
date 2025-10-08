from django.shortcuts import render
from django.conf import settings
import os
from projectrequests.models import ProjectRequest
from engineers.models import Engineer  # استيراد الموديل

def home(request):
    """Home view: portfolio gallery + engineers section."""

    selected_filter = request.GET.get('filter', 'All').lower()

    # 🔹 Portfolio
    qs = ProjectRequest.objects.filter(status__iexact='completed').select_related('file', 'engineer')
    items = []
    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    folder_map = {
        'architecture': 'arch',
        'interior': 'dicor',
        '3d_models': '3d'
    }

    folder = folder_map.get(selected_filter, None)

    if folder:
        folder_dir = os.path.join(getattr(settings, 'MEDIA_ROOT', 'media'), 'projects', folder)
        try:
            files = sorted(os.listdir(folder_dir), reverse=True)
        except Exception:
            files = []

        for fname in files[:4]:
            lower = fname.lower()
            if any(lower.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                items.append({
                    'url': f"{media_url}projects/{folder}/{fname}",
                    'file_type': 'image',
                    'file_name': fname,
                    'category': selected_filter
                })
    else:
        for cat, folder_name in folder_map.items():
            folder_dir = os.path.join(getattr(settings, 'MEDIA_ROOT', 'media'), 'projects', folder_name)
            try:
                files = sorted(os.listdir(folder_dir), reverse=True)
            except Exception:
                files = []

            count = 0
            for fname in files:
                lower = fname.lower()
                if any(lower.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    items.append({
                        'url': f"{media_url}projects/{folder_name}/{fname}",
                        'file_type': 'image',
                        'file_name': fname,
                        'category': cat
                    })
                    count += 1
                    if count >= 4:
                        break

    # 🔹 Engineers section
    engineers = Engineer.objects.filter(status="approved")

    return render(request, 'home.html', {
        'portfolio_items': items,
        'selected_filter': selected_filter,
        'service_images': [
            '/static/images/1.webp',
            '/static/images/2.webp',
            '/static/images/3.webp',
            '/static/images/4.webp'
        ],
        'engineers': engineers,  # إضافة المهندسين للـ template
    })
