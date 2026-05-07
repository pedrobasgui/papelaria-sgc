"""WSGI config for papelaria_sgc project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "papelaria_sgc.settings")
application = get_wsgi_application()
