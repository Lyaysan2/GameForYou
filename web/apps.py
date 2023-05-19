import os

from django.apps import AppConfig

from .ml import init_video_game_model


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
