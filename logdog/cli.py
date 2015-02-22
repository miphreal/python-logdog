"""logdog command line interface

Usage:
  logdog [<pipe-namespace>...] [options]
  logdog (-h | --help)
  logdog --version

Arguments:
  <pipe-namespace>          One or more pipe namespaces to be run

Options:
  -h --help                 Show this screen
  --version                 Show version
  -v --verbose              Run in verbose mode
  -l --log-level=<level>    Set logging level [default: INFO]
  -f --log-format=<format>  Set logging format [default: quiet]
  -c --config=<config>      Configuration file
"""
from docopt import docopt
from logdog.app import Application
from logdog.core.log import configure_logging
from logdog.version import __version__


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

    Application(
        active_parts=arguments.get('<pipe-namespace>'),
        config_path=arguments.get('--config')
    ).run()

if __name__ == '__main__':
    main()