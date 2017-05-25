import os
from django.test.utils import setup_test_environment
import django
from django.core.management import call_command


os.environ.setdefault('DJANGO_SETTINGS_MODULE', "tests.settings")
from .celery import app as celery_app  # noqa

setup_test_environment()
django.setup()
call_command('makemigrations', interactive=False)
call_command('migrate', interactive=False)
