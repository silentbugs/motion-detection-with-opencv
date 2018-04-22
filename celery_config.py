import json

conf = json.load(open('conf.json'))

BROKER_URL = 'amqp://%s:%s@%s/%s' % (
    conf['rabbitmq_user'],
    conf['rabbitmq_password'],
    conf['rabbitmq_host_url'],
    conf['rabbitmq_vhost'],
)
