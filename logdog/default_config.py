# options must be valid python identifiers, e.g. "default_pipe"
# names can be any string, e.g. "file->webui" (excluding ' ', '@')

config = {
    'sources': {
        '/var/log/*.log': {'handler': 'pipes.file-to-webui'},
        '/var/log/*/*.log': {'handler': 'pipes.file-to-webui'},
        '/var/log/syslog': 'pipes.file-to->webui',
    },

    'pipes': {
        'default': 'logdog.core.roles.pipe.Pipe',

        'file-to-webui2': [
            'watch pollers.file-watcher',
            'watch processors.stripper',
            'watch connectors.zmq-tunnel@sender',
            'view connectors.zmq-tunnel@receiver',
            'view viewers.webui',
        ],
        'file-to-webui1': {
            'cls': 'logdog.core.pipe.Pipe',
            '*': [
                'watch pollers.file-watcher',
                'watch,view processors.stripper',
                {'utils.forwarders.round-robbin': [
                    'view viewers.console',
                    [
                        'watch connectors.zmq-tunnel@sender',
                        'view connectors.zmq-tunnel@receiver',
                        {'utils.forwarders.broadcast': [
                            'view viewers.webui',
                            'view viewers.null',
                        ]}
                    ],
                    {}
                ]},
            ],
        }
    },

    # pollers
    'pollers': {
        'file-watcher': {
            'cls': 'logdog.pollers.FileWatcher',
        },
    },

    # collectors
    'collectors': {},

    # processors
    'processors': {
        'stripper': {'cls': 'logdog.processors.Stripper'},
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
        'webui': {
            'cls': 'logdog.viewers.WebUI',
            'port': 8888,
        }
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
    },

    # convention
    'classic-class1a': 'importable.path.to.Class',  # will be converted to `classic-class2a`
    'classic-class2a': {'cls': 'importable.path.to.Class'},

    'classic-class1b': {'kw': 'val'},  # will be converted to `classic-class2bc`
    'classic-class1c': ['val', '...'],  # will be converted to `classic-class2bc`
    'classic-class2bc': {
        'cls': 'will be used fallback parameter (that was specified in the code)',
        # '*': ['val', '...'],  # <- classic-class1b
        # '**': {'kw': 'val'},  # <- classic-class1c
    },

    'classic-class3': {
        'cls': 'importable.path.to.Class or path.inside.the-config',
        '*': [1, 2, 3],  # list of default `*args`
        'kw1': 'val1',  # all other class options that will be passed as `**kwargs`
        'kw2': 'val2',  # ...
        '**': {
            'kw1': 'val1',  # the same as previous lines
            'kw2': 'val2',  # ...
        },
        '@subconf1': {'kw1': 'val1x'},
        '@subconf2': {'kw1': 'val1y'},
    },
}
