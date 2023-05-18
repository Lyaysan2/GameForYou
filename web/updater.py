from apscheduler.schedulers.background import BackgroundScheduler
from .ml import init_video_game_model


def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(init_video_game_model, 'cron', day='*/2', hour=0, minute=0)
    scheduler.start()
