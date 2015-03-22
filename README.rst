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



TODO:

- cover with tests
- zmq connectors
- mongo collector
- webui storages
- webui filtering / searching


Screenshots:

- .. image:: http://i.imgur.com/B4JQ57T.png