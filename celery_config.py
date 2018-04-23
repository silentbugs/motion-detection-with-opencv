import json

conf = json.load(open('conf.json'))

BROKER_URL = 'amqp://%s:%s@%s/%s' % (
    conf['rabbitmq']['user'],
    conf['rabbitmq']['password'],
    conf['rabbitmq']['host'],
    conf['rabbitmq']['vhost'],
)
