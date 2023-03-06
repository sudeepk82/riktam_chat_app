# images/management/commands/createsu.py

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Creates a superuser."

    def handle(self, *args, **options):
        if not User.objects.filter(email="test.admin@example.com").exists():
            User.objects.create_superuser(
                email="test.admin@example.com",
                password=os.getenv("ADMIN_PASSWORD"),
                first_name="Test",
                last_name="Admin",
            )
        print("Superuser has been created.")
