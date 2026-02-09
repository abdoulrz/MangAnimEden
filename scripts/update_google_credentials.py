import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from allauth.socialaccount.models import SocialApp

def update_credentials():
    print("=== Update Google OAuth Credentials ===")
    print("You can find these in your Google Cloud Console (APIs & Services > Credentials).")
    
    client_id = input("Enter your Client ID: ").strip()
    secret = input("Enter your Client Secret: ").strip()

    if not client_id or not secret:
        print("Error: Client ID and Secret cannot be empty.")
        return

    try:
        app = SocialApp.objects.get(provider='google')
        app.client_id = client_id
        app.secret = secret
        app.save()
        print(f"\n✅ Success! Credentials updated for Google Auth.")
        print("You can now try logging in again.")
    except SocialApp.DoesNotExist:
        print("\n❌ Error: Google SocialApp not found. Please run 'python scripts/setup_social_auth.py' first.")

if __name__ == '__main__':
    update_credentials()
