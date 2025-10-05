import random
from django.utils import timezone
from engineers.models import Engineer
from airequests.models import AIRequest
from files.models import File
from models3d.models import Model3D
from sessions_app.models import Session
from users.models import User
from category.models import Category

def random_date(start_days_ago=10, end_days_ago=0):
    delta_days = random.randint(end_days_ago, start_days_ago)
    return timezone.now() - timezone.timedelta(days=delta_days)

def populate_demo_for_eng1_user3():
    try:
        user = User.objects.get(user_id=3)
        engineer = Engineer.objects.get(eng_id=1)
    except (User.DoesNotExist, Engineer.DoesNotExist):
        print("User 3 or Engineer 1 does not exist!")
        return

    # Categories
    categories = list(Category.objects.all())
    if not categories:
        cat_names = ["Bedroom", "Bathroom", "Kitchen", "Living Room"]
        categories = [Category.objects.create(category_name=n) for n in cat_names]

    # 5 AI Requests
    for i in range(5):
        AIRequest.objects.create(
            user=user,
            input_image_path=f"uploads/demo_input_{i+1}.jpg",
            style="Modern",
            output_images_paths=f"outputs/demo_output_{i+1}.jpg",
            status=random.choice(["pending", "completed"]),
        )

    # 5 Files
    for i in range(5):
        File.objects.create(
            user=user,
            file_name=f"portfolio_{i+1}.pdf",
            type="Portfolio",
            path=f"files/portfolio_{i+1}.pdf",
            status=random.choice(["pending", "completed"]),
        )

    # 5 3D Models
    for i in range(5):
        Model3D.objects.create(
            user=user,
            category=random.choice(categories),
            name=f"Model_{i+1}",
            file_path=f"3d_models/model_{i+1}.obj",
        )

    # 5 Sessions
    for i in range(5):
        Session.objects.create(
            user=user,
            eng=engineer,
            scheduled_at=random_date(),
            meeting_link=f"https://zoom.us/demo_session_{i+1}",
            status=random.choice(["pending", "completed"]),
            sessionscol="Consultation",
        )

    print("Demo data populated for Engineer 1 and User 3 ✅")
