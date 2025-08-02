#!/usr/bin/env python
# webapp/manage.py
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    # --- Dynamic Path Configuration ---
    # Add the absolute path to the hushh_mcp project root to sys.path
    # This is CRITICAL for Django to find the agent modules.
    hushh_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if hushh_root not in sys.path:
        sys.path.insert(0, hushh_root)
    # --------------------------------

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_settings.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
