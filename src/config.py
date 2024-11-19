import logging
import os
from logging.config import dictConfig

PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_DB = os.getenv("POSTGRES_DB")
PG_TEST_DB = f"{PG_DB}_test"
DATABASE_URL = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'
DATABASE_TEST_URL = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/'
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LOG_DIR = '../logs'

def config_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging_level = logging.INFO
    logging_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
        },
        'handlers': {
            'null': {
                'level': logging_level,
                'class': 'logging.NullHandler',
            },
            'file_celery': {
                'level': logging_level,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'celery.log'),
                'backupCount': 2,
                'formatter': 'standard',
            },
            'file_fastapi': {
                'level': logging_level,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'fastapi.log'),
                'backupCount': 2,
                'formatter': 'standard',
            },
            'console': {
                'level': logging_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'fastapi': {
                'handlers': ['console', 'file_fastapi'],
                'level': logging_level,
            },

            'celery': {
                'handlers': ['console', 'file_celery'],
                'level': logging_level,
            },
        }
    }
    dictConfig(logging_config)
