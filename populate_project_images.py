import os
import random
import django
from django.core.files import File
from django.core.files.base import ContentFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'makan_project.settings')
django.setup()

from projectrequests.models import ProjectRequest

def populate_projects_with_images():
    """Assign sample images to existing completed projects"""
    
    # Get all completed projects
    completed_projects = ProjectRequest.objects.filter(status='completed')
    
    # Image mapping by specialization
    image_mapping = {
        'architecture': ['arch_project_1.jpg', 'arch_project_2.jpg', 'arch_project_3.jpg'],
        'interior': ['interior_project_1.jpg', 'interior_project_2.jpg', 'interior_project_3.jpg'],
        'civil': ['civil_project_1.jpg', 'civil_project_2.jpg', 'civil_project_3.jpg'],
        'mechanical': ['mech_project_1.jpg', 'mech_project_2.jpg', 'mech_project_3.jpg']
    }
    
    projects_updated = 0
    
    for project in completed_projects:
        # Skip if project already has an image
        if project.project_image:
            continue
            
        # Get appropriate images for this specialization
        specialization = project.engineer.specialization
        available_images = image_mapping.get(specialization, ['arch_project_1.jpg'])
        
        # Randomly select an image
        selected_image = random.choice(available_images)
        image_path = os.path.join('media', 'projects', 'images', selected_image)
        
        # Check if the image file exists
        if os.path.exists(image_path):
            # Read the image file
            with open(image_path, 'rb') as img_file:
                # Create a Django File object
                django_file = File(img_file)
                
                # Assign the image to the project
                project.project_image.save(
                    f'project_{project.request_id}_{selected_image}',
                    django_file,
                    save=True
                )
                
                projects_updated += 1
                print(f"Updated Project #{project.request_id} ({specialization}) with {selected_image}")
        else:
            print(f"Image not found: {image_path}")
    
    print(f"\nTotal projects updated: {projects_updated}")
    
    # Show summary
    total_completed = completed_projects.count()
    projects_with_images = completed_projects.exclude(project_image='').count()
    
    print(f"Completed projects: {total_completed}")
    print(f"Projects with images: {projects_with_images}")
    print(f"Projects without images: {total_completed - projects_with_images}")

if __name__ == "__main__":
    populate_projects_with_images()