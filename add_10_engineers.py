import os
import django
from datetime import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'makan_project.settings')  # عدّل حسب اسم المشروع
django.setup()

from engineers.models import Engineer
from files.models import File
from projectrequests.models import ProjectRequest

# المسار الرئيسي للصور
base_path = 'media/projects/'

# خريطة الفولدرات حسب التخصص
folders_map = {
    'architecture': 'arch',
    'interior': 'dicor',
    '3d models': '3d'
}

# استرجاع جميع المهندسين
engineers = Engineer.objects.all()

project_counter = 1

for eng in engineers:
    specialization = eng.specialization.lower()
    
    # تحقق من وجود فولدر للتخصص
    if specialization not in folders_map:
        print(f"⚠️ No folder mapped for specialization {specialization}")
        continue

    folder_path = os.path.join(base_path, folders_map[specialization])
    
    if not os.path.exists(folder_path):
        print(f"⚠️ Folder not found: {folder_path}")
        continue

    # قراءة كل الملفات في الفولدر
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folders_map[specialization], file_name)  # path للـ DB
        file_ext = file_name.split('.')[-1].lower()

        # إنشاء الـ File object
        f = File.objects.create(
            type=file_ext,
            file_name=file_name,
            path=file_path,
            user_id=eng.user_id,  # نفس مستخدم المهندس
            status='completed'
        )

        # إنشاء الـ ProjectRequest
        pr = ProjectRequest.objects.create(
            client_id=eng.user_id,  # هنا مؤقتًا نفس المهندس كمستخدم العميل
            engineer=eng,
            description=f"Sample project for {specialization}",
            file=f,
            status='completed'
        )

        print(f"✅ Added project {pr.request_id} for engineer {eng.eng_id} with file {file_name}")
        project_counter += 1

print("✅ All projects and files added!")
