import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_test_users():
    users_data = [
        {
            'nickname': 'TestAdmin',
            'email': 'testadmin@example.com',
            'password': 'password123',
            'role_admin': True,
            'role_moderator': True,
            'level': 50,
            'role_reader': True
        },
        {
            'nickname': 'TestMod',
            'email': 'testmod@example.com',
            'password': 'password123',
            'role_admin': False,
            'role_moderator': True,
            'level': 25,
            'role_reader': True
        },
        {
            'nickname': 'TestNormal',
            'email': 'testnormal@example.com',
            'password': 'password123',
            'role_admin': False,
            'role_moderator': False,
            'level': 5,
            'role_reader': True
        }
    ]

    print("--- Creating/Updating Test Users ---")
    for data in users_data:
        user, created = User.objects.get_or_create(
            email=data['email'],
            defaults={
                'nickname': data['nickname']
            }
        )
        
        user.set_password(data['password'])
        user.role_admin = data['role_admin']
        user.role_moderator = data['role_moderator']
        user.role_reader = data['role_reader']
        user.level = data['level']
        user.save()
        
        status = "Created" if created else "Updated"
        print(f"[{status}] User: {user.nickname} ({user.email}) - Roles: Admin={user.role_admin}, Mod={user.role_moderator}")

if __name__ == '__main__':
    create_test_users()
