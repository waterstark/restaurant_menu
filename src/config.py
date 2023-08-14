import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = int(os.environ['REDIS_PORT'])

# RABBITMQ_USER = os.environ(['RABBITMQ_USER'])
# RABBITMQ_PASSWORD = os.environ(['RABBITMQ_PASSWORD'])
# RABBITMQ_VHOST = os.environ(['RABBITMQ_VHOST'])
