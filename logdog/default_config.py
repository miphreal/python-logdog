# options must be valid python identifiers, e.g. "default_pipe"
# names can be any string, e.g. "file->webui" (^::,@)

config = {
    'sources': {
        '/var/log/*.log': {'pipe': 'pipes.file->webui'},
        '/var/log/*/*.log': {'pipe': 'pipes.file->webui'},
        '/var/log/syslog': 'pipes.file->webui',
    },

    'default_pipe': 'pipes.file->webui',

    'pipes': {
        'file->webui': [
            'watch::pollers.file-watcher',
            'watch::processors.stripper',
            'watch::connectors.zmq-tunnel@sender',
            'view::connectors.zmq-tunnel@receiver',
            'view::viewers.webui',
        ],
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
    }
}
