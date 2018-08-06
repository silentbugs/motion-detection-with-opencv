import json
from celery import Celery
from mail import send_email

conf = json.load(open('conf.json'))

# setup celery
app = Celery('tasks')
app.config_from_object('celery_config')


@app.task
def exec_notify():
    recipient = conf['mail']['recipient']
    client_name = conf['mail']['client_name']

    if not conf['main']['dry_run']:
        send_email(
            recipient,
            "Security Alert from %s" % client_name,
            "Motion has been detected in %s." % client_name
        )
    else:
        print 'emailing: %s with %s' % (recipient, client_name)
