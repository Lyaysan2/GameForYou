from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from .ml import init_video_game_model
from .parsing import pars_pages


def start():
    scheduler = BackgroundScheduler()
    # time in UTC
    scheduler.add_job(pars_pages, 'cron', day='*/2', hour=21, minute=0)
    scheduler.start()
