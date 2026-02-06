import os
import django
import sys
import traceback

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from catalog.models import Series, Chapter
from reader.models import ReadingProgress

User = get_user_model()

def verify():
    try:
        print("--- Verifying Gamification Logic V3 (Corrected) ---")
        
        # 1. Setup User
        email = "gamer_v3@test.com"
        User.objects.filter(email=email).delete()
        
        user = User.objects.create_user(email=email, password="password", nickname='GamerTestV3')
        user.xp = 90
        user.level = 1
        user.save()
        print(f"User Created: Level {user.level}, XP {user.xp}")

        # 2. Setup Content
        print("Creating Series...")
        if Series.objects.filter(slug="test-series-v3").exists():
             series = Series.objects.get(slug="test-series-v3")
        else:
             series = Series.objects.create(title="Test Series V3", slug="test-series-v3")
        print(f"Series Created: {series}")

        print("Creating Chapter...")
        # Chapter has no slug! Identify by series + number
        if Chapter.objects.filter(series=series, number=1).exists():
             chapter = Chapter.objects.get(series=series, number=1)
        else:
             chapter = Chapter.objects.create(series=series, number=1, title="Test Chapter")
        print(f"Chapter Created: {chapter}")

        # 3. Simulate Reading (Trigger Signal)
        print("Simulating Chapter Completion...")
        ReadingProgress.objects.filter(user=user, chapter=chapter).delete()
        
        progress = ReadingProgress.objects.create(
            user=user,
            chapter=chapter,
            completed=True
        )
        print("ReadingProgress Created.")

        # 4. Verify XP and Level Up
        user.refresh_from_db()
        print(f"New State: Level {user.level}, XP {user.xp}")

        if user.xp == 100 and user.level == 2:
            print("SUCCESS: XP awarded and Level Up occurred.")
        else:
            print(f"FAILURE: XP/Level mismatch. Got Level {user.level}, XP {user.xp}")

        # 5. Verify Progress Data
        data = user.get_level_progress()
        print(f"Progress Data: {data}")
        # Level 2 (100-200 XP). Current 100. Progress 0%.
        if data['percent'] == 0.0:
             print("SUCCESS: Progress Bar correct.")
        else:
             print(f"FAILURE: Progress Bar mismatch. Got {data['percent']}%")

    except Exception:
        print("!!! EXCEPTION CAUGHT !!!")
        traceback.print_exc()

if __name__ == '__main__':
    verify()
