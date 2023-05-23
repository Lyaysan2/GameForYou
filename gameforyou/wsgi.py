"""
WSGI config for gameforyou project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from web.ml import init_video_game_model, plots_by_parameter
from web.parsing import pars_pages

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gameforyou.settings')

application = get_wsgi_application()

# initialize the model on startup
# pars_pages()
init_video_game_model()
plots_by_parameter()