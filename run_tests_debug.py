import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

sys.path.append(os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = 'MangaAnimEden.settings'
django.setup()

TestRunner = get_runner(settings)
test_runner = TestRunner()
failures = test_runner.run_tests(["users.tests.test_badges"])
sys.exit(bool(failures))
