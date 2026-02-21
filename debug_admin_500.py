import os
import sys
import django
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.test import RequestFactory

def debug_render():
    User = get_user_model()
    # Try to find a user, or create a mock one
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = User(nickname="DebugAdmin", email="debug@admin.com", is_superuser=True, is_staff=True, role_admin=True)
    
    users = User.objects.all()
    
    rf = RequestFactory()
    request = rf.get('/admin-panel/users/')
    request.user = admin
    
    try:
        print("Starting render test...")
        content = render_to_string('administration/user_list.html', {
            'users': users,
            'request': request,
            'is_paginated': False,
        })
        print("Render successful! (Length: {})".format(len(content)))
    except Exception as e:
        print("\n!!! RENDER FAILED !!!")
        traceback.print_exc()

if __name__ == "__main__":
    debug_render()
