import os
from .ml import init_video_game_model
from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            # initialize the model on startup
            init_video_game_model()
            # run processes according to scheduler
            from . import updater
            updater.start()
