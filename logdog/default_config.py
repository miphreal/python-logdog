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

    'pipes': {
        'default': 'logdog.pipes.Pipe',

        'to-web': [
            'watch processors.stripper',
            'watch connectors.zmq-tunnel@sender',
            'view connectors.zmq-tunnel@receiver',
            'view viewers.webui',
        ],

        'experiment-x001': {
            'cls': 'logdog.pipes.Pipe',
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
            'cls': 'logdog.pollers.FileWatcher',
            'namespaces': ['watch'],
        },
    },

    # collectors
    'collectors': {},

    # processors
    'processors': {
        'stripper': {'cls': 'logdog.processors.Stripper'},
    },

    # forwarders
    'forwarders': {
        'broadcast': 'logdog.forwarders.Broadcast',
        'round-robin': 'logdog.forwarders.RoundRobin',
    },

    # connectors
    'connectors': {
        'zmq-tunnel': {
            'cls': 'logdog.connectors.ZMQTunnel',
            '@sender': {'socket': 'PUSH', 'connect': ['tcp://localhost:45457']},
            '@receiver': {'socket': 'PULL', 'bind': ['tcp://*:45457']},
        }
    },

    # viewers
    'viewers': {
        'default': 'logdog.viewers.Null',

        'webui': {
            'cls': 'logdog.viewers.WebUI',
            'port': 8888,
        },
        'console': {
            'cls': 'logdog.viewers.Console',
            'redirect_to': 'stdout',
        },
        'null': 'logdog.viewers.Null',
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
