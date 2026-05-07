"""ASGI config for papelaria_sgc project."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "papelaria_sgc.settings")
application = get_asgi_application()
