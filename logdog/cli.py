"""logdog command line interface

Usage:
  logdog (watch | webui) [options]
  logdog (-h | --help)
  logdog --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  -v --verbose              Run in verbose mode.
  -l --log-level=<level>    Set logging level. [default: INFO]
  -f --log-format=<format>  Set logging format. [default: quiet]
  -c --config=<config>      Configuration file.
"""
import logging.config

from docopt import docopt
from logdog.core.config import ConfigLoader
from logdog.version import __version__


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
            }
        }
    })


def main():
    arguments = docopt(__doc__, version='logdog {}'.format(__version__))

    log_level = arguments.get('--log-level').upper()
    log_format = log_custom_format = arguments.get('--log-format')

    if log_format not in ('verbose', 'quiet'):
        log_format = 'custom'

    if arguments.get('--verbose'):
        log_level = 'DEBUG'
        log_format = 'verbose'

    configure_logging(log_level, log_format, log_custom_format)

    if arguments.get('--config'):
        config = ConfigLoader(path=arguments['--config']).load_config()
    else:
        config = ConfigLoader(path=None).load_config(default_only=True)

    if arguments.get('watch'):
        from logdog import dog
        dog.main(config=config)
    elif arguments.get('webui'):
        from logdog import webui
        if arguments.get('--verbose'):
            config.webui.debug = True
        webui.main(config=config)

if __name__ == '__main__':
    main()