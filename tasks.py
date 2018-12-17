import json
import datetime
from celery import Celery
from mail import send_email

conf = json.load(open('conf.json'))

# setup celery
app = Celery('tasks')
app.config_from_object('celery_config')


@app.task
def exec_notify(attachment=None):
    recipient = conf['mail']['recipient']
    client_name = conf['main']['client_name']

    if not conf['main']['dry_run']:
        send_email(
            recipient,
            "Security Alert from %s" % client_name,
            "Motion has been detected in %s, at %s" % (
                client_name,
                str(datetime.datetime.now())
            ),
            attachment=attachment,
        )
    else:
        print 'emailing: %s with %s' % (recipient, client_name)
