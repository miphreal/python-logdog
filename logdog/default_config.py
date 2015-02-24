import os


# options must be valid python identifiers, e.g. "default_pipe"
# names can be any string, e.g. "file->webui"

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
            'processors.stripper',
            'view::viewers.webui',
        ],

        # TODO. support the following format
        'f->webui': [
            {'watch': [
                'pollers.file-watcher',
                'processors.stripper',
            ]},
            'connectors.zmq-tunnel',
            {'view': [
                'viewers.webui',
            ]}
        ]
    },

    # pollers
    'pollers': {
        'file-watcher': {
            'cls': 'logdog.pollers.FileWatcher',
            'poll_sleep_policy': 'utils.sleep-policies.default',
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
            'sender': {'socket': 'PUSH', 'connect': ['tcp://localhost:45457']},
            'receiver': {'socket': 'PULL', 'bind': ['tcp://localhost:45457']},
        }
    },

    # viewers
    'viewers': {
        'webui': {
            'cls': 'logdog.viewers.WebUI',
            'port': 8888,
            'address': '',
            'autoreload': False,
            'debug': False,
            'static_path': os.path.join(os.path.dirname(__file__), 'viewers/webui/static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'viewers/webui/assets/html'),
        }
    },

    # utils
    'utils': {
        'sleep-policies': {
            'default': {
                'cls': 'logdog.core.sleep_policies.DefaultSleepPolicy'
            }
        }
    }
}
