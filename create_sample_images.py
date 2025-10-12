from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

def create_sample_project_images():
    """Create sample project images for different engineering specializations"""
    
    # Create media directory if it doesn't exist
    media_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'images')
    os.makedirs(media_dir, exist_ok=True)
    
    # Image configurations for different specializations
    image_configs = [
        # Architecture projects
        {'name': 'arch_project_1.jpg', 'color': (102, 126, 234), 'text': 'Modern House\nArchitecture'},
        {'name': 'arch_project_2.jpg', 'color': (118, 75, 162), 'text': 'Villa Design\nProject'},
        {'name': 'arch_project_3.jpg', 'color': (79, 109, 245), 'text': 'Commercial\nBuilding'},
        
        # Interior projects
        {'name': 'interior_project_1.jpg', 'color': (240, 147, 251), 'text': 'Living Room\nDesign'},
        {'name': 'interior_project_2.jpg', 'color': (245, 85, 108), 'text': 'Modern Kitchen\nInterior'},
        {'name': 'interior_project_3.jpg', 'color': (255, 94, 139), 'text': 'Bedroom\nMakeover'},
        
        # Civil projects  
        {'name': 'civil_project_1.jpg', 'color': (79, 172, 254), 'text': 'Bridge\nConstruction'},
        {'name': 'civil_project_2.jpg', 'color': (0, 242, 254), 'text': 'Road\nPlanning'},
        {'name': 'civil_project_3.jpg', 'color': (64, 156, 255), 'text': 'Infrastructure\nProject'},
        
        # Mechanical projects
        {'name': 'mech_project_1.jpg', 'color': (67, 233, 123), 'text': 'HVAC System\nDesign'},
        {'name': 'mech_project_2.jpg', 'color': (56, 249, 215), 'text': 'Mechanical\nInstallation'},
        {'name': 'mech_project_3.jpg', 'color': (45, 212, 191), 'text': 'Industrial\nMachinery'},
    ]
    
    # Create images
    for config in image_configs:
        # Create a 800x600 image with gradient background
        img = Image.new('RGB', (800, 600), config['color'])
        draw = ImageDraw.Draw(img)
        
        # Create gradient effect
        for y in range(600):
            # Calculate gradient color
            factor = y / 600
            r = int(config['color'][0] * (1 - factor * 0.3))
            g = int(config['color'][1] * (1 - factor * 0.3))
            b = int(config['color'][2] * (1 - factor * 0.3))
            
            draw.line([(0, y), (800, y)], fill=(r, g, b))
        
        # Add project text
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Get text bounding box
        text_bbox = draw.textbbox((0, 0), config['text'], font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the text
        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        
        # Add text with shadow effect
        draw.text((x+2, y+2), config['text'], fill=(0, 0, 0, 100), font=font)  # Shadow
        draw.text((x, y), config['text'], fill='white', font=font)  # Main text
        
        # Save the image
        img_path = os.path.join(media_dir, config['name'])
        img.save(img_path, 'JPEG', quality=90)
        print(f"Created: {config['name']}")

if __name__ == "__main__":
    # Set up Django environment
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'makan_project.settings')
    import django
    django.setup()
    
    create_sample_project_images()
    print("Sample project images created successfully!")