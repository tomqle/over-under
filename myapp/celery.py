import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')

app = Celery('myapp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://localhost:6379/0'

app.conf.beat_schedule = {
    'get-standings-every-60-seconds': {
        'task': 'leaderboard.tasks.get_season_standings_auto',
        'schedule': 900.0,
        'args': (),
    }
}

app.conf.timezone = 'UTC'

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


#@app.on_after_configure.connect
#def setup_periodic_tasks(sender, **kwargs):
    #sender.add_periodic_task(60.0, get_standings.s(), name='Get NBA standings.')

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

#@app.task(bind=True)
#def get_standings(self):
    #return _get_standings()
