import logging.config


def configure_logging(log_level, log_format, log_custom_format=None):
    log_custom_format = log_custom_format or log_format
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'quiet': {
                'format': '%(asctime)s [%(levelname)s] %(message)s'
            },
            'verbose': {
                'format': 'PID%(process)d %(asctime)s [%(levelname)s:%(name)s:%(lineno)d] %(message)s'
            },
            'custom': {
                'format': log_custom_format
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': log_format
            }
        },
        'loggers': {
            'logdog': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': False,
            },
            'tornado': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': False,
            },
            'zmq': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': False,
            },
        }
    })

