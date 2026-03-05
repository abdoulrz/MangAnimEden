from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from catalog.models import Series, Chapter, Page
import os
import tempfile
import shutil

TEST_MEDIA_DIR = tempfile.mkdtemp()

@override_settings(
    MEDIA_ROOT=TEST_MEDIA_DIR,
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": TEST_MEDIA_DIR},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class CatalogModelDeleteTests(TestCase):
    def setUp(self):
        # Create a dummy image file
        self.dummy_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'file_content',
            content_type='image/jpeg'
        )
        # Create a dummy zip file
        self.dummy_zip = SimpleUploadedFile(
            name='test_file.zip',
            content=b'zip_content',
            content_type='application/zip'
        )
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_DIR, ignore_errors=True)
        
    def test_series_cover_auto_deleted(self):
        series = Series.objects.create(
            title="Test Series Delete", 
            cover=self.dummy_image
        )
        # Verify file exists
        self.assertTrue(os.path.exists(series.cover.path))
        path = series.cover.path
        
        # Delete series
        series.delete()
        
        # Verify file is deleted
        self.assertFalse(os.path.exists(path))

    def test_chapter_source_auto_deleted(self):
        series = Series.objects.create(title="Test Series Zip")
        chapter = Chapter.objects.create(
            series=series,
            number=1,
            source_file=self.dummy_zip
        )
        # Verify file exists
        self.assertTrue(os.path.exists(chapter.source_file.path))
        path = chapter.source_file.path
        
        # Delete chapter
        chapter.delete()
        
        # Verify file is deleted
        self.assertFalse(os.path.exists(path))

    def test_page_image_auto_deleted(self):
        series = Series.objects.create(title="Test Series Page")
        chapter = Chapter.objects.create(series=series, number=1)
        page = Page.objects.create(
            chapter=chapter,
            page_number=1,
            image=self.dummy_image
        )
        # Verify file exists
        self.assertTrue(os.path.exists(page.image.path))
        path = page.image.path
        
        # Delete page
        page.delete()
        
        # Verify file is deleted
        self.assertFalse(os.path.exists(path))
