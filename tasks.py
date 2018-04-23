import json
from celery import Celery
from mail import send_email

conf = json.load(open('conf.json'))

# setup celery
app = Celery('tasks')
app.config_from_object('celery_config')


@app.task
def exec_notify():
    send_email(
        conf['mail']['recipient'],
        "Security Alert from %s" % conf['mail']['client_name'],
        "Motion has been detected in %s." % conf['mail']['client_name']
    )
