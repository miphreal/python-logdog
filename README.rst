python-logdog
-------------

distributed log tail viewer

Why?

- tail log files and forward them to web in runtime
- dynamically parse and process logs
- aggregating and collecting logs
- alerting


Quick start
===========

Running a simple one-host configuration.

.. code-block:: bash

    $ pip install logdog

Help output:

.. code-block:: bash

    $  logdog --help                                                                                                                                   develop 
    logdog command line interface

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


Prepare config file:

.. code-block:: yaml

    # config.yml
    ---
    sources:
      - /var/log/*.log
      - /var/log/*/*.log
      - /var/log/syslog

Please, see `default_config.py <logdog/default_config.py>`_

Start watching:

.. code-block:: bash

    $ logdog --config=config.yml

You can run watching and viewing parts separately:

.. code-block:: bash

    $ logdog watch --config=config.yml
    # another console
    $ logdog view --config=config.yml


Config
======

YAML is used as a main format for writing configuration.

Default config:

.. code-block:: yaml

    ---
    sources:
      # <path-to-file>
      - /var/log/*.log
      - /var/log/*/*.log
      - /var/log/syslog

``sources`` is a list of target files/logs. Alternatively, this section can be re-written the following way:

.. code-block:: yaml

    ---
    sources:
      - /var/log/*.log: pipes.to-web
      - /var/log/*/*.log:
          handler: pipes.to-web
      # ^ note. 4 spaces
      # in case of 2 spaces it will be a key in the list object
      # {'/var/log/*/*.log': None,
      #  'handler': 'pipes.to-web'}
      # but must be {'/var/log/*/*.log': {'handler': 'pipes.to-web'}}
      - /var/log/syslog: {handler: pipes.to-web}

Full ``sources`` format:

.. code-block:: none

    ---
    sources:
      - (path | search pattern)
      # or (`handler`, `watcher`, `meta` are optional)
      - (path | search pattern):
          handler: handler-name # default pipes.to-web
          watcher: watcher-name # default pollers.file-watcher
          meta: a-dictionary-containing-any-meta-info # e.g. {tags: [tag1, tag2]}
      # or
      - (path | search pattern): handler-name
      # or
      - (path | search pattern): {handler: pipes.to-web}
      # or
      - (path | search pattern): {watcher: poller.custom-file-poller}
      # or
      - (path | search pattern): {meta: {tags: [log]}}


Example 1:

.. code-block:: yaml

    ---
    sources:
      - /var/log/syslog: {handler: pipes.to-web, meta: {tags: [syslog]}
      # or
      - /var/log/syslog2:
          handler: pipes.to-web
          meta:
            tags:
              - syslog


Screenshots
===========

.. image:: http://i.imgur.com/B4JQ57T.png


TODO
====

- cover with tests
- detecting new files
- colorize logs
- add documentation
- zmq connectors
- mongodb collector
- webui storages
- webui filtering / searching
