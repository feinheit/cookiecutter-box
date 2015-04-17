from __future__ import absolute_import, unicode_literals
import env
import os
env.read_dotenv()
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
