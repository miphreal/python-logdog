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
  -l --log-level=<level>    Set internal logging level [default: INFO]
  -f --log-format=<format>  Set internal logging format [default: quiet]
  -c --config=<config>      Configuration file (yaml config)
  -s --sources=<file:...>   Force specify files to be watched
  -H --handler=<handler>    Force set handler for all sources
                            (e.g. --handler=viewers.console)
  --reset-indices           Remove current indices (will reset watching state)
"""
from docopt import docopt
from logdog.app import Application
from logdog.core.config import ConfigLoader
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

    config_path = arguments.get('--config')
    loader = ConfigLoader(path=config_path)
    config = loader.load_config(default_only=not config_path)

    Application(
        active_namespaces=arguments.get('<pipe-namespace>'),
        config=config,
        force_handler=arguments.get('--handler'),
        force_sources=arguments.get('--sources'),
        reset_indices=arguments.get('--reset-indices'),
    ).run()


if __name__ == '__main__':
    main()