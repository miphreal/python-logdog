# Default config.
# options/properties must be valid python identifiers, e.g. "default_pipe"
# names can be any string, e.g. "file->webui" (excluding ' ', '@')

config = {
    # Sources format
    # YAML
    # sources:
    #   - (path | search pattern)
    #   # or
    #   # `handler`, `watcher`, `meta` are optional
    #   - (path | search pattern):
    #     handler: handler-name # default pipes.to-web
    #     watcher: watcher-name # default pollers.file-watcher
    #     meta: a-dictionary-containing-any-meta-info # e.g. {tags: [tag1, tag2]}
    #   # or
    #   - (path | search pattern): handler-name
    #   # or
    #   - (path | search pattern): {handler: pipes.to-web}
    #   # or
    #   - (path | search pattern): {watcher: poller.custom-file-poller}
    #   # or
    #   - (path | search pattern): {meta: {tags: [log]}}

    'sources': {
        '/var/log/*.log': {'handler': 'pipes.to-web'},
        '/var/log/*/*.log': {'handler': 'pipes.to-web'},
        '/var/log/syslog': 'pipes.to-web',
    },

    # Pipes format
    # YAML
    # pipes:
    #   pipe-name:
    #     - [namespace,...] pipe-object  # processors.stripper
    #     - ...                          # ns processors.stripper
    #     - ...config                    # ns1,ns2 processors.stripper

    'pipes': {
        'default': 'logdog.roles.pipes.Pipe',

        'to-web': [
            'watch processors.stripper',
            'watch connectors.zmq-tunnel@sender',
            'view connectors.zmq-tunnel@receiver',
            'view viewers.webui',
        ],

        'experiment-x001': {
            'cls': 'logdog.roles.pipes.Pipe',
            '*': [
                'watch processors.stripper',
                {'forwarders.broadcast': [
                    'watch viewers.console',
                    {'pipes.default': [
                        {'watch connectors.zmq-tunnel@sender': {'connect': 'tcp://localhost:7789'}},
                        {'view connectors.zmq-tunnel@receiver': {'bind': 'tcp://*:7789'}},
                        {'view forwarders.round-robin': [
                            'view viewers.webui',
                            'view viewers.null',
                        ]}
                    ]},
                ]},
            ],
        }
    },

    'options': {
        'sources': {
            'default_handler': 'pipes.to-web',
            'default_watcher': 'pollers.file-watcher',
            'index_file': '~/.config/logdog/sources-index.idx'
        }
    },

    # pollers
    'pollers': {
        'file-watcher': {
            'cls': 'logdog.roles.pollers.FileWatcher',
            'namespaces': ['watch'],
        },
    },

    # collectors
    'collectors': {},

    # processors / parsers / formatters
    'processors': {  # transform message
        'stripper': {'cls': 'logdog.roles.processors.Stripper'},
    },
    'parsers': {  # extract meta
        'regex': {'cls': 'logdog.roles.parsers.Regex', 'regex': r''},
    },
    'formatters': {  # add to meta formatted representation of message
        'formatter': {'cls': 'logdog.roles.formatters.Formatter'},
    },

    # forwarders
    'forwarders': {
        'broadcast': 'logdog.roles.forwarders.Broadcast',
        'round-robin': 'logdog.roles.forwarders.RoundRobin',
    },

    # connectors
    'connectors': {
        'zmq-tunnel': {
            'cls': 'logdog.roles.connectors.ZMQTunnel',
            '@sender': {'socket': 'PUSH', 'connect': ['tcp://localhost:45457']},
            '@receiver': {'socket': 'PULL', 'bind': ['tcp://*:45457']},
        }
    },

    # viewers
    'viewers': {
        'default': 'logdog.roles.viewers.Null',

        'webui': {
            'cls': 'logdog.roles.viewers.WebUI',
            'port': 8888,
        },
        'console': {
            'cls': 'logdog.roles.viewers.Console',
            'redirect_to': 'stdout',
        },
        'null': 'logdog.roles.viewers.Null',
    },

    # utils
    'utils': {
        'policies': {
            'growing-sleep': {
                'cls': 'logdog.core.policies.DefaultSleepPolicy'
            },
            'mostly-greedy': {
                'cls': 'logdog.core.policies.GreedyPolicy'
            }
        }
    }
}
