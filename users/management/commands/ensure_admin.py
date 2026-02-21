import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Creates a superuser non-interactively if it doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()
        nickname = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([nickname, email, password]):
            self.stdout.write(self.style.WARNING(
                "Skipping superuser creation: DJANGO_SUPERUSER_USERNAME, "
                "DJANGO_SUPERUSER_EMAIL, or DJANGO_SUPERUSER_PASSWORD not set."
            ))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser already exists: {email}"))
            return

        # Direct creation bypasses validators that reference the removed 'username' field
        user = User(
            email=email,
            nickname=nickname,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            role_admin=True,
        )
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Superuser created: {email}"))
