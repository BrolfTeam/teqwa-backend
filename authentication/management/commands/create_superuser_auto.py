"""
Django management command to create a superuser from environment variables.
This allows automatic superuser creation during deployment without shell access.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a superuser from environment variables if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@teqwa.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Teqwa@Admin2024')
        
        # Check if superuser already exists (check by email since it's the USERNAME_FIELD)
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser with email "{email}" already exists. Skipping creation.'
                )
            )
            return
        
        # Create superuser
        try:
            User.objects.create_superuser(
                email=email,
                username=username,
                password=password,
                first_name='Admin',
                last_name='User',
                role='admin',
                is_verified=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser "{email}"'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating superuser: {str(e)}'
                )
            )
