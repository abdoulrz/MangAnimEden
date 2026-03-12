import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Series

def populate():
    """Calculates and saves metadata for all existing series."""
    series_list = Series.objects.all()
    count = series_list.count()
    print(f"Found {count} series to update.")
    
    for i, series in enumerate(series_list, 1):
        print(f"[{i}/{count}] Updating {series.title}...")
        series.update_metadata()
        
    print("Optimization complete!")

if __name__ == "__main__":
    populate()
