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

Prepare config file:

.. code-block:: yaml

    # config.yml
    ---
    sources:
      - /var/log/*.log
      - /var/log/*/*.log
      - /var/log/syslog

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

YAML is used for configuring tool.

Default config:

.. code-block:: yaml

    # config.yml
    ---
    sources:
      # <path-to-file>
      - /var/log/*.log
      - /var/log/*/*.log
      - /var/log/syslog

``sources`` is a list of target files/logs. Alternatively, this section can be re-written the following way:

.. code-block:: yaml

    # config.yml
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


Screenshots
===========

.. image:: http://i.imgur.com/B4JQ57T.png


TODO
====

- cover with tests
- colorize logs
- add documentation
- zmq connectors
- mongodb collector
- webui storages
- webui filtering / searching
