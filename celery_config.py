import json

conf = json.load(open('conf.json'))

BROKER_URL = 'amqp://%s:%s@localhost:5672/%s' % (
    conf['rabbitmq_user'],
    conf['rabbitmq_password'],
    conf['rabbitmq_vhost'],
)
