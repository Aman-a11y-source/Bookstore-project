# books/management/commands/create_default_superuser.py

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a default superuser if one does not already exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get superuser credentials from environment variables (RECOMMENDED FOR PRODUCTION)
        # These environment variables MUST be set on Render.
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '') # Email can be empty string if not required
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write(self.style.ERROR(
                "DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD environment variables must be set."
            ))
            return

        if not User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'Creating superuser: {username}'))
            try:
                User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists. Skipping creation.'))

