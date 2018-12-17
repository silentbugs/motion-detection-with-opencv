import json
import datetime
import subprocess

from celery import Celery
from mail import send_email

conf = json.load(open('conf.json'))

# setup celery
app = Celery('tasks')
app.config_from_object('celery_config')


@app.task
def exec_notify(attachment=None):
    client_name = conf['main']['client_name']
    message = "Motion has been detected in %s, at %s" % (
        client_name,
        str(datetime.datetime.now())
    )
    if not conf['main']['dry_run']:
        if conf['mail']['enable']:
            notify_email(message, attachment)

        if conf['signal']['enable']:
            notify_signal(message, attachment)


def notify_email(message, attachment=None):
    recipient = conf['mail']['recipient']
    client_name = conf['main']['client_name']

    send_email(
        recipient,
        "Security Alert from %s" % client_name,
        message,
        attachment=attachment,
    )


def notify_signal(message, attachment=None):
    sender = conf['signal']['sender']
    recipient = conf['signal']['recipient']

    command_list = [
        'signal-cli',
        '-u', sender,
        'send',
        recipient,
        '-m', message,
    ]

    if attachment:
        command_list.append('-a')
        command_list.append(attachment)

    subprocess.call(command_list)
