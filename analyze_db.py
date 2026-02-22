import os
import django

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def analyze():
    from users.models import User, Friendship
    from catalog.models import Series, Chapter, Page
    from social.models import Group, Badge, UserBadge
    from reader.models import ReadingProgress
    
    print("\n--- 📊 MANGANIMEDEN DATABASE INVENTORY ---")
    print(f"Users: {User.objects.count()}")
    print(f"Friendships: {Friendship.objects.count()}")
    print(f"Groups: {Group.objects.count()}")
    print("------------------------------------------")
    print(f"Manga Series: {Series.objects.count()}")
    print(f"Chapters: {Chapter.objects.count()}")
    print(f"Pages Extraites: {Page.objects.count()}")
    print("------------------------------------------")
    print(f"Badges Existing: {Badge.objects.count()}")
    print(f"Badges Unlocked by Users: {UserBadge.objects.count()}")
    print(f"Reading Progress logs: {ReadingProgress.objects.count()}")
    print("------------------------------------------\n")

if __name__ == '__main__':
    analyze()
