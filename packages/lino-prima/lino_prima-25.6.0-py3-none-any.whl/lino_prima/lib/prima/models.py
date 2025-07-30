# When a plugin has fixtures, it must also have a models.py file.
# Otherwise pm prep fails with django.core.exceptions.ImproperlyConfigured:
# '/home/luc/work/prima/lino_prima/lib/prima/fixtures' is a default fixture
# directory for the 'prima' app and cannot be listed in settings.FIXTURE_DIRS.
