# rollback_all_migrations.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Renaissance.settings")

import django
django.setup()

from django.core.management import call_command
from django.apps import apps

if __name__ == '__main__':
    app_configs = apps.get_app_configs()
    apps_to_migrate = [app.name for app in app_configs if 'django.' not in app.name]
    apps_to_migrate.sort(reverse=True)  # Optional: reverse to start with custom apps

    for app in apps_to_migrate:
        try:
            call_command('migrate', app, 'zero')
            print(f"Rolled back migrations for {app}")
        except Exception as e:
            print(f"Failed to roll back migrations for {app}: {e}")
