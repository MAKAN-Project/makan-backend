from django.core.management.base import BaseCommand
from users.models import User
from engineers.models import Engineer

class Command(BaseCommand):
    help = 'Populate the database with dummy users and engineers.'

    def handle(self, *args, **options):
        # Create dummy users
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                email=f'user{i}@example.com',
                defaults={
                    'first_name': f'User{i}',
                    'last_name': f'Test{i}',
                    'password': 'pbkdf2_sha256$260000$dummy$dummy',
                    'phone': f'010000000{i}',
                    'address': f'123 Street {i}',
                    'role': 'customer',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))

        # Create dummy engineers
        fields = [
            ('architecture', 'Architect'),
            ('civil', 'Civil Engineer'),
            ('interior', 'Interior Designer'),
            ('mechanical', 'Mechanical Engineer'),
        ]
        for i, (field, title) in enumerate(fields, start=1):
            user, _ = User.objects.get_or_create(
                email=f'engineer{i}@example.com',
                defaults={
                    'first_name': f'Engineer{i}',
                    'last_name': title,
                    'password': 'pbkdf2_sha256$260000$dummy$dummy',
                    'phone': f'011000000{i}',
                    'address': f'456 Engineer St {i}',
                    'role': 'engineer',
                }
            )
            engineer, created = Engineer.objects.get_or_create(
                user=user,
                defaults={
                    'education': field,
                    'status': 'approved',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created engineer: {user.email} ({field})'))
